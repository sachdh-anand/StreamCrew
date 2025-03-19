# StreamCrew 🔬

StreamCrew is a quantum computing research and presentation platform that leverages AI to automate the research process and generate engaging keynote speeches. Built with CrewAI and Streamlit, this application allows you to explore any research topic with the click of a button.

![StreamCrew Interface](https://images.unsplash.com/photo-1635070041078-e363dbe005cb?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=2070&q=80)

## ✨ Features

- **AI-Powered Research**: Automatically searches the web for the latest information on your topic
- **Keynote Speech Generation**: Creates professional, ready-to-deliver speeches based on research findings
- **Modern UI**: Clean, responsive interface with real-time progress tracking
- **Customizable Topics**: Research any topic of interest, with quantum computing as the default
- **Persistent Results**: All research summaries and speeches are saved for future reference

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher
- An API key from [Serper Dev](https://serper.dev/api-key) for web search capabilities

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/StreamCrew.git
   cd StreamCrew
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   
   # On Windows
   .\venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. Install the package in development mode:
   ```bash
   pip install -e .
   ```

4. Create a `.env` file in the project root with your API keys:
   ```
   SERPER_API_KEY=your_serper_api_key_here
   ```

### Running the Application

Start the Streamlit interface:

```bash
cd src/ui
streamlit run app.py
```

Or alternatively:

```bash
python -m streamlit run src/ui/app.py
```

The application will be available at http://localhost:8501

## 📊 How It Works

StreamCrew uses a two-agent system powered by CrewAI:

1. **Research Agent**: Searches the internet for the latest information on your chosen topic using the SerperDevTool
2. **Writing Agent**: Transforms the research findings into a coherent, engaging keynote speech

The process is fully automated and provides detailed logging of each step, including the web search queries and results.

## 📁 Project Structure

```
StreamCrew/
├── src/                      # Source code
│   ├── agents/               # AI agent definitions
│   ├── config/               # Configuration files
│   ├── models/               # LLM integration
│   ├── ui/                   # Streamlit interface
│   └── utils/                # Utility functions
├── logs/                     # Application logs
├── outputs/                  # Generated research and speeches
├── .env                      # Environment variables (create this)
├── requirements.txt          # Project dependencies
└── setup.py                  # Package configuration
```

## 💻 Usage Examples

1. **Basic Research**:
   - Enter "Quantum Computing Applications in Finance" in the research field
   - Click "Run Research Agent"
   - Wait for the process to complete
   - Review the research summary and keynote speech

2. **Custom Topics**:
   - The system can research any topic, not just quantum computing
   - Try researching emerging technologies, scientific advances, or business trends

## 🛠️ Development

To contribute to StreamCrew:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes: `git commit -m 'Add amazing feature'`
4. Push to the branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👥 Contributors

- StreamCrew Team

## 🔗 References

- [CrewAI](https://docs.crewai.com/) - Framework for orchestrating role-playing, autonomous AI agents
- [Streamlit](https://streamlit.io/) - The fastest way to build data apps
- [Serper Dev](https://serper.dev/) - Google Search API for web research

---

Built with ❤️ using Python, CrewAI, and Streamlit
