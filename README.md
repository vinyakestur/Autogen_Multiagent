# Multi-Agent Architecture Advisory System

A Streamlit-based application that uses AutoGen and Anthropic Claude to provide comprehensive architecture recommendations through specialized AI agents.

## Overview

This system implements a multi-agent architecture where different AI agents specialize in specific domains of software architecture:

- **Head of Architecture**: Strategic oversight and business alignment
- **Cloud Architect**: Cloud platforms, serverless, containers, and distributed systems
- **OSS Architect**: Open source software solutions and licensing
- **Lead Architect**: General architecture patterns and technical leadership

## Features

- Interactive web interface built with Streamlit
- Multi-agent collaboration using AutoGen framework
- Anthropic Claude integration for advanced AI capabilities
- Categorized architecture requests
- Priority-based processing
- Expandable response sections for each agent

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment variables:
```bash
# Create .env file with your Anthropic API key
ANTHROPIC_API_KEY=your_api_key_here
```

3. Run the application:
```bash
streamlit run app.py
```

## Usage

1. Enter your Anthropic API key in the sidebar
2. Describe your architectural challenge in the text area
3. Select relevant categories and priority level
4. Click "Get Architecture Recommendations"
5. Review responses from each specialized agent

## Architecture

The system uses a group chat pattern where:
- A GroupChatManager coordinates between agents
- Each agent has specialized knowledge and system prompts
- Agents collaborate to provide comprehensive recommendations
- User requests are routed to appropriate specialists
