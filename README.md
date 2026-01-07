# 🎨 Mistral Debugger & Logic Analyzer

**Turning complex code into intuitive visual stories.**

Most AI debuggers overwhelm you with walls of text. **Mistral Debugger & Logic Analyzer** takes a different approach: it runs entirely **locally**, detects bugs, and **visualizes code logic** with dynamic diagrams—so you can *see* what your code is actually doing.

Built with a strong focus on **explainable AI**, this tool helps developers understand not just *what* is wrong, but *why*.

---

## ✨ Key Features

* **🖥️ Fully Local Execution**
  Runs on your machine using **Mistral‑7B**—no cloud calls, no API keys, no privacy trade‑offs.

* **📊 Visual Logic Flow**
  Automatically converts control flow into **Mermaid.js diagrams**, making complex branches and loops easy to grasp.

* **🧠 Human‑Centric Explanations**
  Step‑by‑step annotations explain the *reasoning* behind the logic, not just the syntax.

* **⚡ High Performance on Consumer Hardware**
  Optimized with **QLoRA + 4‑bit NF4 quantization** to run on an 8GB GPU.

---

## 🛠️ Tech Stack

| Layer               | Technology                                             |
| ------------------- | ------------------------------------------------------ |
| **Model (Brain)**   | Mistral‑7B‑Instruct‑v0.2 (QLoRA fine‑tuned)            |
| **Frontend**        | Streamlit (customized UI)                              |
| **Visualization**   | Mermaid.js (live rendering)                            |
| **Analysis Engine** | Python (AST parsing, metadata & complexity extraction) |

---

## 🧠 Model & Training Philosophy

The core of this project is a **specialized language model**, not a general‑purpose chatbot.

### 🎯 Goal: A Code Logic Specialist

Instead of broad conversational ability, the model is optimized to:

* Detect logical fallacies and edge cases
* Understand control flow deeply
* Emit **structured, machine‑readable outputs**

### 🤖 Fine‑Tuning with QLoRA

To enable local inference on consumer hardware:

* **Quantization**: 4‑bit NormalFloat (NF4)
* **Training Method**: QLoRA
* **Dataset**: Project CodeNet

  * Millions of Java and Python samples
  * Emphasis on algorithmic reasoning and control flow

### 🔑 The “Secret Sauce”

During fine‑tuning, the model was explicitly trained to output **structured metadata blocks**.

This allows the Python backend to:

* Reliably extract Mermaid syntax
* Prevent malformed diagrams
* Keep the UI stable and predictable

---

## 🚀 Getting Started

### 1️⃣ Model Weights

Due to GitHub file size limits, model weights are not included.

* **Download**: Mistral‑7B‑Instruct‑v0.2 (GGUF format)
* **Place weights in**:

```text
/mistral_7b_instruct_v2_4bit/
```

---

### 2️⃣ Run the Application

#### Install dependencies

```bash
pip install -r requirements.txt
```

#### Launch Streamlit

```bash
streamlit run main.py
```

The app will be available at:

```
http://localhost:8501
```

---

## 🎥 Inside the App: How It Works

When you paste a code snippet, the system performs a **three‑stage analysis**:

### 1️⃣ Metadata Extraction

* Programming language detection
* Filename inference
* Algorithm / pattern identification

### 2️⃣ Logic Flow Visualization

* Control paths converted into **Mermaid diagrams**
* Clear representation of:

  * Conditionals
  * Loops
  * Branching execution paths

### 3️⃣ Annotated Fix & Analysis

* Corrected or optimized code
* Line‑by‑line explanations
* Time & space complexity analysis (e.g. `O(n)`, `O(log n)`)

---

## 🎯 Why This Project Matters

Debugging is often the **most time‑consuming** part of software development. This project is built to:

* Reduce cognitive load
* Improve code comprehension
* Make debugging more visual, intuitive, and human‑friendly

Instead of staring at logs, you **see the story your code is telling**.

---

## 📜 License

MIT License

---

**Built for developers who want clarity, not just correctness.**
