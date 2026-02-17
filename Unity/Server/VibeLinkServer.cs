using UnityEngine;
using System;
using System.Net;
using System.Net.Sockets;
using System.Text;
using System.Threading;
using System.Collections.Concurrent;
using System.Collections.Generic;
using System.Security.Cryptography;
using System.Text.RegularExpressions;
using System.Linq;

[DefaultExecutionOrder(-100)]
[ExecuteAlways] // <-- Vital para correr en Edit Mode
public class VibeLinkServer : MonoBehaviour
{
    [Header("Server Settings")]
    public int port = 8085;
    public bool autoStart = true;
    
    private TcpListener tcpListener;
    private Thread serverThread;
    private bool isRunning = false;
    
    private ConcurrentQueue<Action> mainThreadActions = new ConcurrentQueue<Action>();
    private List<TcpClient> clients = new List<TcpClient>();

    public static VibeLinkServer Instance { get; private set; }

    void OnEnable()
    {
        if (Instance == null) Instance = this;
        
        if (Application.isPlaying)
        {
            DontDestroyOnLoad(gameObject);
        }

        #if UNITY_EDITOR
        UnityEditor.EditorApplication.update += UpdateQueue;
        #endif

        if (autoStart) StartServer();
    }

    void OnDisable()
    {
        #if UNITY_EDITOR
        UnityEditor.EditorApplication.update -= UpdateQueue;
        #endif
        StopServer();
    }

    // En Runtime usamos Update normal
    void Update()
    {
        if (Application.isPlaying) ProcessQueue();
    }

    #if UNITY_EDITOR
    void UpdateQueue()
    {
        if (!Application.isPlaying) ProcessQueue();
    }
    #endif

    void ProcessQueue()
    {
        int processed = 0;
        while (mainThreadActions.TryDequeue(out Action action))
        {
            try { action.Invoke(); }
            catch (Exception e) { Debug.LogError($"[VibeLink] Error: {e}"); }
            
            processed++;
            if (processed > 50) break;
        }
    }

    public void StartServer()
    {
        if (isRunning) return;

        try
        {
            tcpListener = new TcpListener(IPAddress.Any, port);
            tcpListener.Start();
            
            isRunning = true;
            serverThread = new Thread(AcceptClientsLoop);
            serverThread.IsBackground = true;
            serverThread.Start();
            
            Debug.Log($"[VibeLink] Server started on port {port}");
        }
        catch (Exception e)
        {
            Debug.LogError($"[VibeLink] Failed to start: {e.Message}");
        }
    }

    public void StopServer()
    {
        isRunning = false;
        if (tcpListener != null) tcpListener.Stop();
        
        lock(clients)
        {
            foreach(var c in clients) c.Close();
            clients.Clear();
        }
    }

    private void AcceptClientsLoop()
    {
        while (isRunning)
        {
            try
            {
                if (!tcpListener.Pending())
                {
                    Thread.Sleep(100);
                    continue;
                }
                
                TcpClient client = tcpListener.AcceptTcpClient();
                ThreadPool.QueueUserWorkItem(HandleClient, client);
            }
            catch (Exception e) 
            {
                if (isRunning) Debug.LogError($"[VibeLink] Accept error: {e.Message}");
            }
        }
    }

    // --- WebSocket Logic ---

    private void HandleClient(object obj)
    {
        TcpClient client = (TcpClient)obj;
        NetworkStream stream = client.GetStream();
        
        try
        {
            // 1. Handshake
            if (!PerformHandshake(stream))
            {
                client.Close();
                return;
            }

            lock(clients) clients.Add(client);
            Debug.Log("[VibeLink] Client connected!");

            // 2. Read Loop
            while (client.Connected)
            {
                string msg = ReadFrame(stream);
                if (msg == null) break; // Connection closed
                
                // Encolar acción en Main Thread
                string capturedMsg = msg; // Capture for lambda
                mainThreadActions.Enqueue(() => ProcessCommand(capturedMsg, client));
            }
        }
        catch (Exception)
        {
            // Disconnected
        }
        finally
        {
            lock(clients) clients.Remove(client);
            client.Close();
            Debug.Log("[VibeLink] Client disconnected");
        }
    }

    private bool PerformHandshake(NetworkStream stream)
    {
        byte[] buffer = new byte[4096]; // Suficiente para headers
        int bytesRead = stream.Read(buffer, 0, buffer.Length);
        string header = Encoding.UTF8.GetString(buffer, 0, bytesRead);

        if (Regex.IsMatch(header, "^GET", RegexOptions.IgnoreCase))
        {
            // Extraer key
            Match match = Regex.Match(header, "Sec-WebSocket-Key: (.*)");
            if (!match.Success) return false;
            
            string swk = match.Groups[1].Value.Trim();
            string swka = swk + "258EAFA5-E914-47DA-95CA-C5AB0DC85B11";
            byte[] swkaSha1 = SHA1.Create().ComputeHash(Encoding.UTF8.GetBytes(swka));
            string swkaSha1Base64 = Convert.ToBase64String(swkaSha1);

            string response = "HTTP/1.1 101 Switching Protocols\r\n" +
                              "Connection: Upgrade\r\n" +
                              "Upgrade: websocket\r\n" +
                              "Sec-WebSocket-Accept: " + swkaSha1Base64 + "\r\n\r\n";
            
            byte[] responseBytes = Encoding.UTF8.GetBytes(response);
            stream.Write(responseBytes, 0, responseBytes.Length);
            return true;
        }
        return false;
    }

    private string ReadFrame(NetworkStream stream)
    {
        int b1 = stream.ReadByte(); if (b1 == -1) return null;
        int b2 = stream.ReadByte(); if (b2 == -1) return null;

        bool fin = (b1 & 0x80) != 0;
        int opcode = b1 & 0x0F; // 1 = text, 8 = close

        if (opcode == 8) return null; // Close frame

        bool masked = (b2 & 0x80) != 0;
        long payloadLen = b2 & 0x7F;

        if (payloadLen == 126)
        {
            byte[] lenBytes = new byte[2];
            stream.Read(lenBytes, 0, 2);
            if (BitConverter.IsLittleEndian) Array.Reverse(lenBytes);
            payloadLen = BitConverter.ToUInt16(lenBytes, 0);
        }
        else if (payloadLen == 127)
        {
            byte[] lenBytes = new byte[8];
            stream.Read(lenBytes, 0, 8);
            if (BitConverter.IsLittleEndian) Array.Reverse(lenBytes);
            payloadLen = (long)BitConverter.ToUInt64(lenBytes, 0); // Cast to long (risk of overflow but unlikely for JSON)
        }

        byte[] maskingKey = new byte[4];
        if (masked)
        {
            stream.Read(maskingKey, 0, 4);
        }

        byte[] payload = new byte[payloadLen];
        int totalRead = 0;
        while (totalRead < payloadLen)
        {
            int read = stream.Read(payload, totalRead, (int)payloadLen - totalRead);
            if (read == -1) return null; // connection lost
            totalRead += read;
        }

        if (masked)
        {
            for (int i = 0; i < payloadLen; i++)
            {
                payload[i] = (byte)(payload[i] ^ maskingKey[i % 4]);
            }
        }

        return Encoding.UTF8.GetString(payload);
    }

    public void Broadcast(string message)
    {
        lock(clients)
        {
            // Limpiar clientes desconectados
            clients.RemoveAll(c => !c.Connected);
            
            foreach(var client in clients)
            {
                SendFrame(client, message);
            }
        }
    }

    public void SendFrame(TcpClient client, string message)
    {
        try
        {
            byte[] payload = Encoding.UTF8.GetBytes(message);
            List<byte> frame = new List<byte>();

            frame.Add(0x81); // Fin + Text Opcode

            if (payload.Length <= 125)
            {
                frame.Add((byte)payload.Length);
            }
            else if (payload.Length >= 126 && payload.Length <= 65535)
            {
                frame.Add(126);
                frame.Add((byte)((payload.Length >> 8) & 0xFF));
                frame.Add((byte)(payload.Length & 0xFF));
            }
            else
            {
                frame.Add(127);
                frame.Add(0); frame.Add(0); frame.Add(0); frame.Add(0); // 4 bytes padding (64bit length unsupported for now)
                frame.Add((byte)((payload.Length >> 24) & 0xFF));
                frame.Add((byte)((payload.Length >> 16) & 0xFF));
                frame.Add((byte)((payload.Length >> 8) & 0xFF));
                frame.Add((byte)(payload.Length & 0xFF));
            }

            frame.AddRange(payload);
            byte[] buffer = frame.ToArray();
            
            NetworkStream stream = client.GetStream();
            stream.Write(buffer, 0, buffer.Length);
        }
        catch (Exception e)
        {
            Debug.LogError($"[VibeLink] Send error: {e.Message}");
        }
    }

    private void ProcessCommand(string json, TcpClient client)
    {
        // Ejecutado en Main Thread
        string response = "";
        try
        {
            // Debug.Log($"[VibeLink] Cmd: {json}"); // Loguear todo puede ser ruidoso
            
            if (json.Contains("dump_hierarchy"))
            {
                response = HierarchyDumper.DumpScene();
            }
            else if (json.Contains("ping"))
            {
                response = "{\"status\": \"pong\"}";
            }
            else
            {
                // Relay: Si no es un comando interno de Unity, reenviarlo a los clientes (Blender)
                // Esto permite que un script externo (Agente) controle Blender a través de Unity
                Broadcast(json);
                response = "{\"status\": \"relayed\"}";
                Debug.Log($"[VibeLink] Relayed command: {json}");
            }
        }
        catch (Exception e)
        {
            response = $"{{\"error\": \"{e.Message}\"}}";
            Debug.LogError($"[VibeLink] Cmd Error: {e}");
        }

        // Responder en el hilo del socket (si es seguro) o en otro thread
        // TcpClient.GetStream().Write es thread-safe en .NET? Generalmente sí.
        // Pero mejor lanzarlo a un Task para no bloquear el Main Thread con I/O.
        
        string resp = response; // capture
        ThreadPool.QueueUserWorkItem((_) => SendFrame(client, resp));
    }
}
