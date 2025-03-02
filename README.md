# Confession Wall Project

Welcome to the **Confession Wall Project**! 🚀

This project aims to create a **distributed chat network**. Our channel provides a unique and anonymous **confession wall**, where users can post confessions, react to others, and comment to open a discussion while ensuring a safe and moderated environment.

---

## 📑 Table of Contents
1. 🔑 Key Features
2. ⚙️ How It Works
   - Home Route
   - Confession Submission & Interaction
   - Message Filtering
   - Message Expiry & Limitations
3. 🛠️ Tech Stack
4. 🚀 Getting Started
5. 📂 Project Structure
6. 🌟 Enjoy the Confession Wall!
7. 📝 Attribution

---

## 🔑 Key Features
- ✅ **Anonymous Confessions** - Post messages using an alias to prevent revealing your identity.
- ✅ **React & Comment** - Engage with confessions by leaving comments and three types of reactions.
- ✅ **Auto-Expiring Messages** - Confessions disappear after **24 hours** to keep the wall fresh.
- ✅ **Message Limitation** - Only the latest **100 confessions** are stored.
- ✅ **Content Moderation** - A filter removes inappropriate words to maintain a respectful environment.
- ✅ **Active Channel** - Auto-generated responses for specific message patterns.
- ✅ **Channel List** - Browse other chat channels from the distributed hub using our channel list.

---

## ⚙️ How It Works

## ⚙️ How It Works

### 1️⃣ Home Route
When you visit our channel, you will see:
- A **welcome message** introducing the purpose of the confession wall. When you select another channel, a standardized welcome message and layout will be used. 
- A **personalized greeting**: Users must enter their name upon arrival, which will then be displayed in a personalized greeting message.
- A **list of the most recent confessions** (newest at the top, oldest at the bottom).
- A **channel list** on the left to explore other public chat channels.

### 2️⃣ Confession Submission & Interaction
Users can submit confessions anonymously. Others can:
- **Like/react** to a confession with three different options/buttons/emojis.
- **Comment** on a confession (using the `extra` field to attach comments).

### 3️⃣ Message Filtering
To ensure a respectful and meaningful discussion:
- A **profanity filter** removes inappropriate words before posting.
- Off-topic or spam messages are **not displayed**.
- Automatic **keyword-based responses** e.g.:
  - **Short messages** → "That was short but impactful"
  - **Long messages** → "Wow, thanks for the long submission!"
  - **Emotional messages** (e.g., "lonely") → "You are not alone… thanks for being part of the community."

### 4️⃣ Message Expiry & Limitations
- **Messages disappear after 24 hours** to keep discussions fresh.
- **Only the latest 15 messages** are displayed, ensuring a clean and relevant feed.

---

## 🛠️ Tech Stack
- **Python**: Backend logic and message handling
- **Flask**: Web server framework
- **React (JavaScript)**: Frontend UI for chat interaction
- **WebSockets**: Real-time messaging functionality
- **Profanity Filter**: Ensures appropriate language use
- **University Distributed Hub**: Connects to other chat channels

---

## 🚀 Getting Started
### 1️⃣ Clone the Repository:
```bash
 git clone https://github.com/iritter/ChatNetwork.git
```
### 2️⃣ Install Dependencies:
```bash
 pip install -r requirements.txt
```
### 3️⃣ Run the Channel Server:
```bash
 python channel.py
```
### 4️⃣ Deploy & Register:
- Register it with the **public hub** at:
  - **Hub endpoint**: `http://vm146.rz.uni-osnabrueck.de/hub`
  - **Auth key**: `Pssst it's a secret`

---

## 📂 Project Structure
```
ChatNetwork/
|   .gitignore
|   README.md
|   requirements.txt
|   channel.py
|   hub.py
|   react.html
|   messages.json
|   channel.wsgi
|   hub.wsgi
|
|   styles.css
|
+---templates
|       channel.html
|       home.html
```

---

## 🌟 Enjoy the Confession Wall!
We hope you enjoy using our **anonymous confession wall**! 💬💖
Share your thoughts, interact with others, and be part of this safe and engaging community!

---

## 📝 Attribution
Created with ❤️ by Group 11: Johanna, Christina & Isabel. 
