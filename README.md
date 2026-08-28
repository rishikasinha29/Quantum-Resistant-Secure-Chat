
# 🔐 Quantum-Resistant Secure Chat

### Secure Messaging using CRYSTALS-Kyber / ML-KEM and AES-256-GCM

A GUI-based secure chat application demonstrating the integration of **Post-Quantum Cryptography (PQC)** with authenticated symmetric encryption for secure real-time communication.

The system uses **CRYSTALS-Kyber / ML-KEM** for post-quantum key establishment and **AES-256-GCM** for secure message encryption. A **PyQt5** interface provides the user-facing chat application, while **SQLite** is used for local message logging.

---

## 📌 Table of Contents

- [Overview](#-overview)
- [Objectives](#-objectives)
- [Key Features](#-key-features)
- [System Architecture](#-system-architecture)
- [Communication Workflow](#-communication-workflow)
- [Cryptographic Design](#-cryptographic-design)
- [Project Structure](#-project-structure)
- [Technologies Used](#-technologies-used)
- [Prerequisites](#-prerequisites)
- [Installation](#-installation)
- [Running the Application](#-running-the-application)
- [Testing the Application](#-testing-the-application)
- [Security Properties](#-security-properties)
- [Limitations](#-limitations)
- [Future Enhancements](#-future-enhancements)
- [Project Team](#-project-team)
- [License](#-license)

---

## 📖 Overview

Traditional public-key cryptographic algorithms such as **RSA** and **ECC** are potentially vulnerable to sufficiently powerful quantum computers because of quantum algorithms such as **Shor's algorithm**.

**Post-Quantum Cryptography (PQC)** aims to develop cryptographic mechanisms that can provide security against both classical and quantum-computing threats.

This project implements a **Quantum-Resistant Secure Chat Application** that combines a post-quantum key establishment mechanism with authenticated symmetric encryption.

### Main Components

- **CRYSTALS-Kyber / ML-KEM** – Post-quantum key establishment
- **AES-256-GCM** – Authenticated symmetric encryption
- **PyQt5** – Graphical user interface
- **TCP Sockets** – Network communication
- **SQLite** – Local message logging
- **Python** – Core implementation

The application follows a client-server architecture where the server acts as a **relay** and forwards encrypted packets between clients.

---

## 🎯 Objectives

The main objectives of this project are:

1. Demonstrate the practical implementation of **Post-Quantum Cryptography**.
2. Implement **Kyber / ML-KEM** for post-quantum key establishment.
3. Establish a shared secret between communicating clients.
4. Derive a symmetric encryption key from the established shared secret.
5. Use **AES-256-GCM** for authenticated message encryption.
6. Develop a simple and user-friendly secure chat interface.
7. Implement real-time communication using TCP sockets.
8. Maintain locally stored chat history using SQLite.
9. Demonstrate the integration of PQC into a real-time communication application.

---

## ✨ Key Features

### 🔑 Post-Quantum Key Establishment

- PQC-based Key Encapsulation Mechanism (KEM)
- Kyber / ML-KEM support
- Public/private key generation
- Public-key exchange
- KEM encapsulation
- KEM decapsulation
- Shared-secret establishment

### 🔒 Secure Message Encryption

- AES-256-GCM encryption
- Unique nonce for each message
- Authentication tag
- Ciphertext integrity verification
- Detection of modified or tampered messages

### 💬 Chat Interface

- PyQt5-based GUI
- Real-time messaging
- Connection status
- Secure-session status
- Chat history display

### 🌐 Networking

- TCP client-server communication
- Relay-server architecture
- JSON-based communication protocol
- Encrypted message transmission

### 🗄️ Local Database

- SQLite-based message storage
- Timestamped messages
- Sent/received message information
- Local chat history

---

## 🏗️ System Architecture

                  ┌──────────────────────┐
                  │       CLIENT A       │
                  │                      │
                  │      PyQt5 GUI       │
                  │          │           │
                  │          ▼           │
                  │      ML-KEM/Kyber    │
                  │          │           │
                  │          ▼           │
                  │      AES-256-GCM      │
                  └──────────┬───────────┘
                             │
                             │ Encrypted TCP
                             │
                             ▼
                  ┌──────────────────────┐
                  │     RELAY SERVER     │
                  │                      │
                  │  • Accept Clients    │
                  │  • Forward Packets   │
                  │  • No Decryption     │
                  └──────────┬───────────┘
                             │
                             │ Encrypted TCP
                             │
                             ▼
                  ┌──────────────────────┐
                  │       CLIENT B       │
                  │                      │
                  │      PyQt5 GUI       │
                  │          │           │
                  │          ▼           │
                  │      ML-KEM/Kyber    │
                  │          │           │
                  │          ▼           │
                  │      AES-256-GCM      │
                  └──────────────────────┘


---

## 🔄 Communication Workflow

### 1. Client Startup

Both clients connect to the relay server.

```text
Client A ──────────► Relay Server
Client B ──────────► Relay Server
```

---

### 2. PQC Key Generation

Each client generates a post-quantum key pair:

```text
           PQC Key Generation
                  │
          ┌───────┴───────┐
          ▼               ▼
     Public Key       Private Key
```

The private key remains on the respective client.

---

### 3. Public-Key Exchange

The clients exchange their public keys through the relay server.

```text
Client A
   │
   │ Public Key
   ▼
Server
   │
   │ Public Key
   ▼
Client B
```

---

### 4. KEM Encapsulation

A client uses the peer's public key to perform KEM encapsulation.

The operation produces:

```text
KEM Ciphertext
      +
Shared Secret
```

The KEM ciphertext is transmitted to the peer.

---

### 5. KEM Decapsulation

The receiving client uses its private key to decapsulate the KEM ciphertext.

Both clients obtain the same shared secret.

```text
Client A ───── Shared Secret ───── Client B
```

---

### 6. AES Key Derivation

The shared secret is processed to obtain a 256-bit symmetric encryption key.

```text
PQC Shared Secret
        │
        ▼
    Key Derivation
        │
        ▼
    AES-256 Key
```

---

### 7. Message Encryption

When a user sends a message, the plaintext is encrypted using AES-256-GCM.

```text
Plaintext
    │
    ▼
AES-256-GCM
    │
    ▼
Nonce + Ciphertext + Authentication Tag
```

---

### 8. Message Transmission

The encrypted packet is transmitted through the relay server.

```text
Client A
   │
   │ Encrypted Packet
   ▼
Server
   │
   │ Encrypted Packet
   ▼
Client B
```

The relay server forwards the packet without requiring access to the plaintext message.

---

### 9. Message Decryption

The receiving client verifies the authentication tag and decrypts the ciphertext.

```text
Encrypted Packet
       │
       ▼
Authentication Verification
       │
       ▼
AES-256-GCM Decryption
       │
       ▼
Plaintext
```

---

## 🔐 Cryptographic Design

### Post-Quantum Cryptography

The project uses the **Kyber / ML-KEM** family for post-quantum key establishment.

Depending on the installed LibOQS version, the algorithm may be exposed as:

```text
Kyber768
```

or:

```text
ML-KEM-768
```

The KEM allows the communicating clients to establish a common shared secret without directly transmitting that secret over the network.

---

### Symmetric Encryption

After the PQC handshake, the established shared secret is used to derive a symmetric encryption key.

The resulting key is used with:

```text
AES-256-GCM
```

AES-GCM provides:

* Confidentiality
* Integrity
* Authentication

---

## 🔒 AES-256-GCM Message Structure

An encrypted message conceptually contains:

```text
┌─────────────────────────────┐
│            Nonce            │
├─────────────────────────────┤
│          Ciphertext         │
├─────────────────────────────┤
│     Authentication Tag      │
└─────────────────────────────┘
```

The authentication tag allows the receiver to verify that the encrypted message has not been modified.

---

## 📁 Project Structure

```text
Quantum_Resistant_Secure_Chat/
│
├── client_gui.py
├── crypto.py
├── database.py
├── protocol.py
├── server.py
├── run_demo.py
├── requirements.txt
└── README.md
```

After running the application, SQLite database files may also be generated:

```text
Quantum_Resistant_Secure_Chat/
│
├── Alice_chat.db
├── Bob_chat.db
└── ...
```

---

## 📄 File Descriptions

| File               | Description                                            |
| ------------------ | ------------------------------------------------------ |
| `client_gui.py`    | Main PyQt5 client application and chat interface       |
| `crypto.py`        | PQC/KEM and AES-256-GCM cryptographic operations       |
| `database.py`      | SQLite database management and message logging         |
| `protocol.py`      | Network packet framing and JSON communication protocol |
| `server.py`        | TCP relay server                                       |
| `run_demo.py`      | Utility script for running the demonstration           |
| `requirements.txt` | Python package dependencies                            |
| `README.md`        | Project documentation                                  |

---

## 🛠️ Technologies Used

| Technology         | Purpose                        |
| ------------------ | ------------------------------ |
| **Python**         | Application development        |
| **LibOQS**         | Post-Quantum Cryptography      |
| **Kyber / ML-KEM** | Post-quantum key establishment |
| **PyCryptodome**   | AES-256-GCM encryption         |
| **PyQt5**          | Graphical user interface       |
| **SQLite**         | Local database                 |
| **TCP Sockets**    | Network communication          |
| **JSON**           | Communication protocol         |

---

## 💻 Prerequisites

Before running the application, make sure the following are installed:

* Python 3.10 or later
* pip
* PyQt5
* PyCryptodome
* LibOQS
* Python bindings for LibOQS

Check your Python version:

```bash
python --version
```

On Linux/Kali Linux:

```bash
python3 --version
```

---

## ⚙️ Installation

### 1. Clone the Repository

```bash
git clone <YOUR-GITHUB-REPOSITORY-URL>
```

Navigate to the project directory:

```bash
cd Quantum_Resistant_Secure_Chat
```

---

### 2. Create a Virtual Environment

#### Windows

```powershell
python -m venv venv
```

Activate it:

```powershell
venv\Scripts\activate
```

#### Linux / Kali Linux

```bash
python3 -m venv venv
```

Activate it:

```bash
source venv/bin/activate
```

---

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 🧩 Verify LibOQS

Test whether the OQS Python module is available:

```bash
python -c "import oqs; print('OQS installed successfully')"
```

Check the available KEM algorithms:

```bash
python -c "import oqs; print(oqs.get_enabled_kem_mechanisms())"
```

Look for an available Kyber/ML-KEM implementation such as:

```text
Kyber768
```

or:

```text
ML-KEM-768
```

---

## 🧪 Test the Cryptographic Module

Run:

```bash
python -c "from crypto import PQCKEM; k=PQCKEM(); print('Algorithm:', k.algorithm)"
```

If the cryptographic module is configured correctly, the selected PQC algorithm should be displayed.

---

## ▶️ Running the Application

The application requires:

1. One relay server
2. Client A
3. Client B

All three can be run on the same computer for local testing.

---

### Step 1 — Start the Server

Open a terminal inside the project directory:

```bash
python server.py
```

The server should start listening on the configured port.

Example:

```text
[SERVER] Relay server started.
[SERVER] Listening on 0.0.0.0:5000
```

Keep this terminal open.

---

### Step 2 — Start Client A

Open a second terminal.

Activate the virtual environment if required:

```powershell
venv\Scripts\activate
```

Run:

```bash
python client_gui.py --name Alice
```

The PyQt5 chat interface should open.

---

### Step 3 — Start Client B

Open a third terminal.

Activate the virtual environment:

```powershell
venv\Scripts\activate
```

Run:

```bash
python client_gui.py --name Bob
```

A second chat window should open.

---

## 🔐 Secure Session Establishment

After both clients connect, the application performs the PQC handshake.

The terminal may display messages similar to:

```text
PQC key pair generated
PQC public key transmitted
Received peer public key
PQC encapsulation completed
KEM ciphertext sent
PQC decapsulation completed
AES-256-GCM session established
```

Once the handshake is complete, the clients can exchange encrypted messages.

---

## 💬 Testing the Application

### Send a Message

In Alice's window, type:

```text
Hello Bob!
```

Click **Send**.

Bob should receive the message.

Bob can then respond:

```text
Hello Alice!
```

Alice should receive the response.

---

## 🧪 Security Testing

### Test 1 — Normal Communication

Send multiple messages between the two clients.

Expected result:

```text
Messages are successfully encrypted,
transmitted, authenticated and decrypted.
```

---

### Test 2 — Multiple Messages

Exchange several messages in both directions.

Expected result:

```text
All valid messages are displayed correctly.
```

---

### Test 3 — Ciphertext Modification

Modify the ciphertext or authentication tag before decryption.

Expected result:

```text
Authentication failure
```

The modified message should not be accepted as valid plaintext.

---

### Test 4 — Client Disconnection

Close one client.

Expected result:

```text
Peer disconnected
```

The remaining client should detect the connection termination.

---

## 🗄️ Database and Chat History

The application uses **SQLite** for local message storage.

A database may be created for each client, for example:

```text
Alice_chat.db
Bob_chat.db
```

Depending on the implementation, stored information may include:

* Message ID
* Timestamp
* Sender
* Receiver
* Message direction
* Message content

Example:

| Direction | Peer | Message      |
| --------- | ---- | ------------ |
| Sent      | Bob  | Hello Bob!   |
| Received  | Bob  | Hello Alice! |

---

## 🖥️ Debugging

Cryptographic and networking information is displayed in the terminal.

Example:

```text
PQC key pair generated
PQC public key transmitted
Received peer PQC public key
PQC encapsulation completed
KEM ciphertext sent
PQC decapsulation completed
AES-256-GCM session established
Encrypted message transmitted
Message authentication verified
```

Private keys and session keys should **not** be printed or exposed during normal operation.

---

## 🔐 Security Properties

#### Confidentiality

Messages are encrypted using AES-256-GCM before being transmitted.

#### Integrity

AES-GCM authentication tags allow modified ciphertexts to be detected.

#### Post-Quantum Key Establishment

The session establishment process uses a Kyber/ML-KEM based KEM rather than relying exclusively on traditional RSA/ECC key exchange.

#### Private-Key Protection

The PQC private key remains on the client and is not intentionally transmitted to the relay server.

#### Relay Server

The relay server is designed to forward encrypted communication packets rather than process plaintext chat messages.

---

## ⚠️ Security Considerations

This project is an **academic and research prototype**.

It should **not** be considered a production-ready secure messaging system without additional security engineering, testing, and independent security auditing.

A production implementation would require additional mechanisms such as:

* Strong user authentication
* Identity verification
* Digital signatures
* Key fingerprints
* Mutual authentication
* Key rotation
* Replay protection
* Secure key storage
* Rate limiting
* Secure memory handling
* Formal protocol analysis
* Security auditing

---

## ⚠️ Important Cryptographic Note

The project focuses primarily on:

```text
Kyber / ML-KEM
       +
AES-256-GCM
```

References to other post-quantum algorithms such as **Dilithium** or **Falcon** should not be interpreted as implemented functionality unless corresponding implementation code has been added to the project.

---

## 🚧 Limitations

The current prototype has the following limitations:

1. It is intended primarily for academic demonstration.
2. The communication model is limited to the supported client configuration.
3. Production-grade identity verification is not implemented.
4. Complete digital-signature-based authentication is not implemented.
5. Group messaging is not implemented.
6. Voice and video communication are not implemented.
7. Mobile clients are not implemented.
8. Formal third-party security auditing has not been performed.
9. The relay server is intended for demonstration purposes.
10. Local SQLite chat history is not necessarily encrypted at rest.

---

## 🚀 Future Enhancements

Possible future improvements include:

#### 📱 Mobile Application

Develop Android and iOS versions of the secure chat application.

#### 👥 Group Chat

Implement secure multi-party/group communication.

#### 🪪 Digital Identity

Introduce stronger identity verification and digital signatures.

#### 🔄 Key Rotation

Implement automatic session-key rotation.

#### 🛡️ Hybrid Cryptography

Support hybrid classical + post-quantum key establishment.

#### 🔐 Encrypted Database

Protect locally stored chat history using database encryption.

#### 🎙️ Secure Voice/Video

Extend the platform to support encrypted audio and video communication.

#### 🌐 Scalable Server Architecture

Develop a scalable infrastructure capable of supporting a larger number of concurrent users.

---

## 📊 Complete System Flow

```text
                    ┌─────────────────────┐
                    │    Start Client     │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Generate PQC Keys   │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Exchange Public     │
                    │       Keys          │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ KEM Encapsulation   │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │   Shared Secret     │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Derive AES-256 Key  │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │   AES-256-GCM       │
                    │    Encryption       │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Encrypted Message   │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │    TCP Relay        │
                    │      Server         │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Authentication      │
                    │ Verification        │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ AES-GCM Decryption  │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │   Display Message   │
                    │      in GUI         │
                    └─────────────────────┘
```

---

## 👥 Project Team

| S. No. | Name              | Contribution                 |
| -----: | ----------------- | ---------------------------- |
|      1 | **Rishika Sinha** | Model Building, PPT, Journal |
|      2 | **Aditi Dixit**   | PPT, Journal                 |

#### Supervisor

**Dr. Komarasamy G**
Senior Associate Professor (Grade-1)
School of Computing Science, Engineering and Artificial Intelligence
VIT Bhopal University

---

## 📜 License

This project is developed primarily for **academic and educational purposes**.

The project may contain third-party libraries and cryptographic implementations that are subject to their respective licenses.

Users intending to deploy or distribute the project should review the licenses and security requirements of all dependencies.

---

## ⭐ Acknowledgement

This project was developed to explore the practical integration of **Post-Quantum Cryptography into secure real-time communication**.

The implementation demonstrates how a PQC-based key establishment mechanism can be combined with authenticated symmetric encryption to create a prototype secure communication system.

---

## 🔐 Quantum-Resistant Secure Chat

**CRYSTALS-Kyber / ML-KEM + AES-256-GCM + PyQt5**

> A demonstration of Post-Quantum Cryptography integrated with secure real-time communication.

```
```
