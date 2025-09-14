# requirements.txt
"""
streamlit
pyautogen
anthropic
python-dotenv
pandas
"""

import streamlit as st
import autogen
from anthropic import Anthropic
import os
from dotenv import load_dotenv
import json
from typing import Dict, List, Any
import pandas as pd
import datetime
import networkx as nx
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import numpy as np
import io
import base64

# Load environment variables
load_dotenv()

class AnthropicConfig:
    """Configuration for Anthropic API with AutoGen"""
    
    @staticmethod
    def get_config():
        return {
            "model": "claude-3-5-sonnet-20240620",
            "api_key": os.getenv("ANTHROPIC_API_KEY"),
            "api_type": "anthropic",
            "temperature": 0.7,
            "max_tokens": 2000,
        }

class ArchitectureAgents:
    """Define all the architecture agents from your diagram"""
    
    def __init__(self):
        self.config = AnthropicConfig.get_config()
        self.agents = {}
        self.setup_agents()
    
    def setup_agents(self):
        """Initialize all agents with their specific roles"""
        
        # Head of Architecture - Supervisory role
        self.agents["head_of_architecture"] = autogen.AssistantAgent(
            name="HeadOfArchitecture",
            system_message="""You are the Head of Architecture. Your role is to:
            1. Analyze business requirements and architectural needs
            2. Coordinate with specialized architects
            3. Ensure architectural decisions align with business goals
            4. Provide high-level guidance and oversight
            5. Make final architectural recommendations
            
            Always think strategically about scalability, maintainability, and business impact.""",
            llm_config=self.config
        )
        
        # Cloud Architect
        self.agents["cloud_architect"] = autogen.AssistantAgent(
            name="CloudArchitect",
            system_message="""You are a Cloud Architect specialist. Your expertise includes:
            1. Cloud platforms (AWS, Azure, GCP)
            2. Serverless architectures
            3. Container orchestration (Kubernetes, Docker)
            4. Cloud security and compliance
            5. Cost optimization strategies
            6. Microservices and distributed systems
            
            Provide detailed cloud-specific solutions and recommendations.""",
            llm_config=self.config
        )
        
        # OSS (Open Source Software) Architect
        self.agents["oss_architect"] = autogen.AssistantAgent(
            name="OSSArchitect", 
            system_message="""You are an Open Source Software Architect. Your expertise includes:
            1. Open source technology stacks
            2. License compatibility and compliance
            3. Community-driven development practices
            4. Cost-effective open source solutions
            5. Integration of OSS with proprietary systems
            6. Security considerations for open source components
            
            Focus on leveraging open source solutions effectively.""",
            llm_config=self.config
        )
        
        # Lead Architect
        self.agents["lead_architect"] = autogen.AssistantAgent(
            name="LeadArchitect",
            system_message="""You are a Lead Architect with broad technical expertise:
            1. System design and architecture patterns
            2. Technology selection and evaluation
            3. Performance and scalability considerations
            4. Integration strategies
            5. Risk assessment and mitigation
            6. Technical leadership and mentoring
            
            Provide comprehensive architectural guidance across all domains.""",
            llm_config=self.config
        )
        
        # User Proxy (represents the business/user)
        self.agents["user_proxy"] = autogen.UserProxyAgent(
            name="BusinessUser",
            human_input_mode="NEVER",
            code_execution_config=False,
            system_message="You represent the business requirements and user needs."
        )

    def create_group_chat(self):
        """Create the group chat manager from your diagram"""
        
        agent_list = list(self.agents.values())
        
        group_chat = autogen.GroupChat(
            agents=agent_list,
            messages=[],
            max_round=5,  # One round per agent (4 agents + 1 user proxy)
            speaker_selection_method="round_robin"
        )
        
        # Add termination condition to stop after each agent speaks once
        def should_terminate(messages):
            # Count unique agent responses (excluding user proxy)
            agent_responses = set()
            for msg in messages:
                if msg.get("name") and msg.get("name") != "BusinessUser":
                    agent_responses.add(msg.get("name"))
            # Terminate when all 4 agents have spoken
            return len(agent_responses) >= 4
        
        group_chat_manager = autogen.GroupChatManager(
            groupchat=group_chat,
            llm_config=self.config,
            system_message="""You are the Group Chat Manager coordinating between architectural specialists.
            Route conversations to the most appropriate expert based on the technical domain:
            - Cloud-related questions → Cloud Architect
            - Open source questions → OSS Architect  
            - General architecture → Lead Architect
            - Strategic decisions → Head of Architecture
            
            Ensure all perspectives are considered before final recommendations."""
        )
        
        return group_chat_manager, group_chat

class ArchitectureReportGenerator:
    """Generate comprehensive reports from agent conversations"""
    
    def __init__(self):
        self.agent_roles = {
            "HeadOfArchitecture": "Strategic Oversight",
            "CloudArchitect": "Cloud Infrastructure", 
            "OSSArchitect": "Open Source Solutions",
            "LeadArchitect": "Technical Integration",
            "BusinessUser": "Business Requirements"
        }
    
    def extract_key_recommendations(self, messages: List[Dict]) -> Dict[str, List[str]]:
        """Extract key recommendations from each agent's response"""
        recommendations = {}
        
        for msg in messages:
            agent_name = msg.get("name", "Unknown")
            content = msg.get("content", "")
            
            if agent_name == "BusinessUser" or not content.strip():
                continue
                
            # Extract key points from each agent's response
            key_points = self._extract_key_points(content)
            recommendations[agent_name] = key_points
            
        return recommendations
    
    def _extract_key_points(self, content: str) -> List[str]:
        """Extract key points from agent content"""
        # Simple extraction - look for numbered lists, bullet points, and key phrases
        lines = content.split('\n')
        key_points = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Look for numbered lists (1., 2., etc.)
            if line.startswith(('1.', '2.', '3.', '4.', '5.', '6.', '7.', '8.', '9.')):
                key_points.append(line)
            # Look for bullet points
            elif line.startswith(('-', '•', '*', '→')):
                key_points.append(line)
            # Look for key phrases
            elif any(keyword in line.lower() for keyword in ['recommend', 'suggest', 'propose', 'consider', 'implement', 'use', 'deploy']):
                if len(line) < 200:  # Avoid very long lines
                    key_points.append(line)
        
        return key_points[:10]  # Limit to top 10 points per agent
    
    def generate_summary_table(self, messages: List[Dict], user_request: str, categories: List[str], priority: str) -> pd.DataFrame:
        """Generate a comprehensive summary table"""
        
        recommendations = self.extract_key_recommendations(messages)
        
        # Create summary data
        summary_data = []
        
        for agent_name, key_points in recommendations.items():
            role = self.agent_roles.get(agent_name, "Unknown Role")
            
            # Combine key points into a single string
            combined_points = "\n".join(key_points[:5]) if key_points else "No specific recommendations provided"
            
            # Count recommendations
            rec_count = len(key_points)
            
            summary_data.append({
                "Agent": agent_name,
                "Role": role,
                "Key Recommendations": combined_points,
                "Recommendation Count": rec_count,
                "Focus Area": self._get_focus_area(agent_name)
            })
        
        return pd.DataFrame(summary_data)
    
    def _get_focus_area(self, agent_name: str) -> str:
        """Get the focus area for each agent"""
        focus_areas = {
            "HeadOfArchitecture": "Strategic Planning & Business Alignment",
            "CloudArchitect": "Cloud Infrastructure & Scalability", 
            "OSSArchitect": "Open Source Tools & Cost Optimization",
            "LeadArchitect": "Technical Integration & Architecture Patterns"
        }
        return focus_areas.get(agent_name, "General Architecture")
    
    def generate_detailed_report(self, messages: List[Dict], user_request: str, categories: List[str], priority: str) -> Dict:
        """Generate a detailed report with multiple sections"""
        
        recommendations = self.extract_key_recommendations(messages)
        
        report = {
            "metadata": {
                "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "user_request": user_request,
                "categories": categories,
                "priority": priority,
                "total_agents": len(recommendations),
                "total_recommendations": sum(len(points) for points in recommendations.values())
            },
            "agent_summaries": {},
            "key_insights": [],
            "implementation_roadmap": [],
            "risk_assessment": [],
            "cost_considerations": []
        }
        
        # Process each agent's recommendations
        for agent_name, key_points in recommendations.items():
            role = self.agent_roles.get(agent_name, "Unknown Role")
            
            report["agent_summaries"][agent_name] = {
                "role": role,
                "recommendations": key_points,
                "count": len(key_points),
                "focus_area": self._get_focus_area(agent_name)
            }
        
        # Extract key insights
        report["key_insights"] = self._extract_insights(messages)
        
        # Generate implementation roadmap
        report["implementation_roadmap"] = self._generate_roadmap(recommendations)
        
        # Extract risk assessment
        report["risk_assessment"] = self._extract_risks(messages)
        
        # Extract cost considerations
        report["cost_considerations"] = self._extract_cost_considerations(messages)
        
        return report
    
    def _extract_insights(self, messages: List[Dict]) -> List[str]:
        """Extract key insights from the conversation"""
        insights = []
        all_content = " ".join([msg.get("content", "") for msg in messages])
        
        # Look for insight keywords
        insight_keywords = ["insight", "key finding", "important", "critical", "essential", "crucial", "significant"]
        
        for msg in messages:
            content = msg.get("content", "")
            if any(keyword in content.lower() for keyword in insight_keywords):
                # Extract sentences containing insight keywords
                sentences = content.split('.')
                for sentence in sentences:
                    if any(keyword in sentence.lower() for keyword in insight_keywords):
                        if len(sentence.strip()) > 20:
                            insights.append(sentence.strip())
        
        return insights[:5]  # Top 5 insights
    
    def _generate_roadmap(self, recommendations: Dict[str, List[str]]) -> List[Dict]:
        """Generate implementation roadmap based on recommendations"""
        roadmap = []
        
        phases = [
            {"phase": "Phase 1: Foundation", "duration": "2-4 weeks", "description": "Core infrastructure setup"},
            {"phase": "Phase 2: Development", "duration": "4-8 weeks", "description": "Application development and integration"},
            {"phase": "Phase 3: Testing", "duration": "2-3 weeks", "description": "Testing and quality assurance"},
            {"phase": "Phase 4: Deployment", "duration": "1-2 weeks", "description": "Production deployment and monitoring"}
        ]
        
        return phases
    
    def _extract_risks(self, messages: List[Dict]) -> List[str]:
        """Extract risk assessment from messages"""
        risks = []
        
        for msg in messages:
            content = msg.get("content", "")
            if any(keyword in content.lower() for keyword in ["risk", "challenge", "concern", "issue", "problem", "limitation"]):
                # Extract risk-related sentences
                sentences = content.split('.')
                for sentence in sentences:
                    if any(keyword in sentence.lower() for keyword in ["risk", "challenge", "concern", "issue", "problem"]):
                        if len(sentence.strip()) > 20:
                            risks.append(sentence.strip())
        
        return risks[:5]  # Top 5 risks
    
    def _extract_cost_considerations(self, messages: List[Dict]) -> List[str]:
        """Extract cost considerations from messages"""
        costs = []
        
        for msg in messages:
            content = msg.get("content", "")
            if any(keyword in content.lower() for keyword in ["cost", "budget", "price", "expensive", "cheap", "affordable", "optimization"]):
                # Extract cost-related sentences
                sentences = content.split('.')
                for sentence in sentences:
                    if any(keyword in sentence.lower() for keyword in ["cost", "budget", "price", "expensive", "cheap", "affordable"]):
                        if len(sentence.strip()) > 20:
                            costs.append(sentence.strip())
        
        return costs[:5]  # Top 5 cost considerations

class DynamicGraphGenerator:
    """Generate dynamic graphs and visualizations from architecture recommendations"""
    
    def __init__(self):
        self.colors = {
            'cloud': '#FF6B6B',
            'database': '#4ECDC4', 
            'api': '#45B7D1',
            'service': '#96CEB4',
            'storage': '#FFEAA7',
            'security': '#DDA0DD',
            'monitoring': '#98D8C8',
            'user': '#F7DC6F'
        }
    
    def extract_architecture_components(self, messages: List[Dict]) -> Dict[str, List[str]]:
        """Extract architecture components from agent messages"""
        components = {
            'cloud_services': [],
            'databases': [],
            'apis': [],
            'microservices': [],
            'storage': [],
            'security': [],
            'monitoring': [],
            'user_interfaces': []
        }
        
        # Keywords to identify different component types
        keywords = {
            'cloud_services': ['aws', 'azure', 'gcp', 'cloud', 'serverless', 'lambda', 'ec2', 's3', 'rds', 'kubernetes', 'docker'],
            'databases': ['database', 'db', 'postgresql', 'mysql', 'mongodb', 'redis', 'elasticsearch', 'dynamodb', 'sql', 'nosql'],
            'apis': ['api', 'rest', 'graphql', 'gateway', 'endpoint', 'service mesh'],
            'microservices': ['microservice', 'service', 'container', 'pod', 'deployment'],
            'storage': ['storage', 'file', 'blob', 's3', 'bucket', 'cdn'],
            'security': ['security', 'auth', 'authentication', 'authorization', 'ssl', 'tls', 'encryption'],
            'monitoring': ['monitoring', 'logging', 'metrics', 'observability', 'prometheus', 'grafana'],
            'user_interfaces': ['ui', 'frontend', 'web', 'mobile', 'react', 'angular', 'vue']
        }
        
        for msg in messages:
            content = msg.get("content", "").lower()
            agent_name = msg.get("name", "")
            
            for component_type, keyword_list in keywords.items():
                for keyword in keyword_list:
                    if keyword in content:
                        # Extract the full phrase containing the keyword
                        sentences = content.split('.')
                        for sentence in sentences:
                            if keyword in sentence and len(sentence.strip()) > 10:
                                components[component_type].append(sentence.strip())
        
        # Remove duplicates and limit results
        for component_type in components:
            components[component_type] = list(set(components[component_type]))[:5]
        
        return components
    
    def create_architecture_diagram(self, components: Dict[str, List[str]], user_request: str) -> go.Figure:
        """Create an interactive architecture diagram using Plotly"""
        
        # Create a network graph
        G = nx.Graph()
        
        # Add central node for the main application
        G.add_node("Main Application", node_type="application", size=20, color=self.colors['service'])
        
        # Add components as nodes
        node_positions = {}
        node_info = {}
        
        # Position nodes in a circular layout around the main application
        center_x, center_y = 0, 0
        radius = 3
        
        # Add cloud services
        for i, service in enumerate(components['cloud_services']):
            angle = (2 * 3.14159 * i) / max(len(components['cloud_services']), 1)
            x = center_x + radius * 1.5 * np.cos(angle)
            y = center_y + radius * 1.5 * np.sin(angle)
            node_id = f"Cloud_{i}"
            G.add_node(node_id, node_type="cloud", size=15, color=self.colors['cloud'])
            node_positions[node_id] = (x, y)
            node_info[node_id] = service[:50] + "..." if len(service) > 50 else service
            G.add_edge("Main Application", node_id)
        
        # Add databases
        for i, db in enumerate(components['databases']):
            angle = (2 * 3.14159 * i) / max(len(components['databases']), 1)
            x = center_x + radius * 2 * np.cos(angle)
            y = center_y + radius * 2 * np.sin(angle)
            node_id = f"DB_{i}"
            G.add_node(node_id, node_type="database", size=12, color=self.colors['database'])
            node_positions[node_id] = (x, y)
            node_info[node_id] = db[:50] + "..." if len(db) > 50 else db
            G.add_edge("Main Application", node_id)
        
        # Add microservices
        for i, service in enumerate(components['microservices']):
            angle = (2 * 3.14159 * i) / max(len(components['microservices']), 1)
            x = center_x + radius * 1 * np.cos(angle)
            y = center_y + radius * 1 * np.sin(angle)
            node_id = f"Service_{i}"
            G.add_node(node_id, node_type="microservice", size=10, color=self.colors['service'])
            node_positions[node_id] = (x, y)
            node_info[node_id] = service[:50] + "..." if len(service) > 50 else service
            G.add_edge("Main Application", node_id)
        
        # Add APIs
        for i, api in enumerate(components['apis']):
            angle = (2 * 3.14159 * i) / max(len(components['apis']), 1)
            x = center_x + radius * 0.5 * np.cos(angle)
            y = center_y + radius * 0.5 * np.sin(angle)
            node_id = f"API_{i}"
            G.add_node(node_id, node_type="api", size=8, color=self.colors['api'])
            node_positions[node_id] = (x, y)
            node_info[node_id] = api[:50] + "..." if len(api) > 50 else api
            G.add_edge("Main Application", node_id)
        
        # Set main application position
        node_positions["Main Application"] = (center_x, center_y)
        node_info["Main Application"] = "Main Application"
        
        # Create edge traces
        edge_x = []
        edge_y = []
        for edge in G.edges():
            x0, y0 = node_positions[edge[0]]
            x1, y1 = node_positions[edge[1]]
            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])
        
        edge_trace = go.Scatter(
            x=edge_x, y=edge_y,
            line=dict(width=2, color='#888'),
            hoverinfo='none',
            mode='lines'
        )
        
        # Create node traces
        node_x = []
        node_y = []
        node_text = []
        node_colors = []
        node_sizes = []
        
        for node in G.nodes():
            x, y = node_positions[node]
            node_x.append(x)
            node_y.append(y)
            node_text.append(node_info[node])
            node_colors.append(G.nodes[node]['color'])
            node_sizes.append(G.nodes[node]['size'])
        
        node_trace = go.Scatter(
            x=node_x, y=node_y,
            mode='markers+text',
            hoverinfo='text',
            text=node_text,
            textposition="middle center",
            marker=dict(
                size=node_sizes,
                color=node_colors,
                line=dict(width=2, color='white')
            )
        )
        
        # Create the figure
        fig = go.Figure(data=[edge_trace, node_trace],
                       layout=go.Layout(
                           title=f'Architecture Diagram: {user_request[:50]}...',
                           titlefont_size=16,
                           showlegend=False,
                           hovermode='closest',
                           margin=dict(b=20,l=5,r=5,t=40),
                           annotations=[ dict(
                               text="Interactive Architecture Diagram - Hover over nodes for details",
                               showarrow=False,
                               xref="paper", yref="paper",
                               x=0.005, y=-0.002,
                               xanchor="left", yanchor="bottom",
                               font=dict(color="gray", size=12)
                           )],
                           xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                           yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                           plot_bgcolor='white'
                       ))
        
        return fig
    
    def create_component_distribution_chart(self, components: Dict[str, List[str]]) -> go.Figure:
        """Create a pie chart showing component distribution"""
        
        component_counts = {k: len(v) for k, v in components.items() if v}
        
        if not component_counts:
            # Create empty chart if no components
            fig = go.Figure()
            fig.add_annotation(text="No components identified", xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False)
            return fig
        
        labels = [k.replace('_', ' ').title() for k in component_counts.keys()]
        values = list(component_counts.values())
        colors = [self.colors.get(k.split('_')[0], '#95A5A6') for k in component_counts.keys()]
        
        fig = go.Figure(data=[go.Pie(
            labels=labels,
            values=values,
            marker_colors=colors,
            textinfo='label+percent',
            textfont_size=12
        )])
        
        fig.update_layout(
            title="Architecture Components Distribution",
            titlefont_size=16,
            showlegend=True
        )
        
        return fig
    
    def create_implementation_timeline(self, detailed_report: Dict) -> go.Figure:
        """Create a Gantt chart for implementation timeline"""
        
        phases = detailed_report.get("implementation_roadmap", [])
        
        if not phases:
            fig = go.Figure()
            fig.add_annotation(text="No implementation timeline available", xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False)
            return fig
        
        # Create Gantt chart data
        tasks = []
        start_dates = []
        durations = []
        colors = []
        
        for i, phase in enumerate(phases):
            tasks.append(phase['phase'])
            start_dates.append(i * 2)  # Start week
            durations.append(2)  # Duration in weeks
            colors.append(px.colors.qualitative.Set3[i % len(px.colors.qualitative.Set3)])
        
        fig = go.Figure(data=[go.Bar(
            x=durations,
            y=tasks,
            orientation='h',
            marker_color=colors,
            text=[f"{phase['duration']}" for phase in phases],
            textposition='inside'
        )])
        
        fig.update_layout(
            title="Implementation Timeline",
            xaxis_title="Duration (weeks)",
            yaxis_title="Phase",
            height=300,
            showlegend=False
        )
        
        return fig
    
    def create_risk_priority_matrix(self, detailed_report: Dict) -> go.Figure:
        """Create a risk priority matrix"""
        
        risks = detailed_report.get("risk_assessment", [])
        
        if not risks:
            fig = go.Figure()
            fig.add_annotation(text="No risks identified", xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False)
            return fig
        
        # Simple risk scoring (in a real implementation, this would be more sophisticated)
        risk_data = []
        for i, risk in enumerate(risks):
            # Simple scoring based on keywords
            impact = 3 if any(word in risk.lower() for word in ['critical', 'severe', 'major']) else 2
            probability = 3 if any(word in risk.lower() for word in ['likely', 'probable', 'common']) else 2
            
            risk_data.append({
                'Risk': f"Risk {i+1}",
                'Impact': impact,
                'Probability': probability,
                'Description': risk[:100] + "..." if len(risk) > 100 else risk
            })
        
        df = pd.DataFrame(risk_data)
        
        fig = px.scatter(
            df, 
            x='Probability', 
            y='Impact',
            size=[10] * len(df),
            hover_data=['Description'],
            title="Risk Priority Matrix"
        )
        
        fig.update_layout(
            xaxis_title="Probability",
            yaxis_title="Impact",
            height=400
        )
        
        return fig

def generate_markdown_report(detailed_report: Dict, summary_table: pd.DataFrame) -> str:
    """Generate a comprehensive markdown report"""
    
    metadata = detailed_report["metadata"]
    
    markdown_content = f"""# Multi-Agent Architecture Advisory Report

**Generated:** {metadata['timestamp']}  
**Request:** {metadata['user_request']}  
**Categories:** {', '.join(metadata['categories'])}  
**Priority:** {metadata['priority']}  
**Total Agents:** {metadata['total_agents']}  
**Total Recommendations:** {metadata['total_recommendations']}

---

## 📋 Agent Recommendations Summary

| Agent | Role | Focus Area | Recommendation Count |
|-------|------|------------|---------------------|
"""
    
    # Add summary table rows
    for _, row in summary_table.iterrows():
        markdown_content += f"| {row['Agent']} | {row['Role']} | {row['Focus Area']} | {row['Recommendation Count']} |\n"
    
    markdown_content += "\n---\n\n## 🔍 Key Insights\n\n"
    
    # Add key insights
    if detailed_report["key_insights"]:
        for i, insight in enumerate(detailed_report["key_insights"], 1):
            markdown_content += f"{i}. {insight}\n"
    else:
        markdown_content += "No specific insights extracted from the conversation.\n"
    
    markdown_content += "\n---\n\n## ⚠️ Risk Assessment\n\n"
    
    # Add risk assessment
    if detailed_report["risk_assessment"]:
        for i, risk in enumerate(detailed_report["risk_assessment"], 1):
            markdown_content += f"{i}. {risk}\n"
    else:
        markdown_content += "No specific risks identified in the conversation.\n"
    
    markdown_content += "\n---\n\n## 💰 Cost Considerations\n\n"
    
    # Add cost considerations
    if detailed_report["cost_considerations"]:
        for i, cost in enumerate(detailed_report["cost_considerations"], 1):
            markdown_content += f"{i}. {cost}\n"
    else:
        markdown_content += "No specific cost considerations mentioned.\n"
    
    markdown_content += "\n---\n\n## 📈 Implementation Roadmap\n\n"
    
    # Add implementation roadmap
    for phase in detailed_report["implementation_roadmap"]:
        markdown_content += f"### {phase['phase']}\n"
        markdown_content += f"**Duration:** {phase['duration']}\n"
        markdown_content += f"**Description:** {phase['description']}\n\n"
    
    markdown_content += "\n---\n\n## 📊 Detailed Agent Recommendations\n\n"
    
    # Add detailed agent recommendations
    for agent_name, agent_data in detailed_report["agent_summaries"].items():
        markdown_content += f"### {agent_name} - {agent_data['role']}\n"
        markdown_content += f"**Focus Area:** {agent_data['focus_area']}\n"
        markdown_content += f"**Recommendation Count:** {agent_data['count']}\n\n"
        
        if agent_data['recommendations']:
            markdown_content += "**Key Recommendations:**\n"
            for i, rec in enumerate(agent_data['recommendations'], 1):
                markdown_content += f"{i}. {rec}\n"
        else:
            markdown_content += "No specific recommendations provided.\n"
        
        markdown_content += "\n---\n\n"
    
    markdown_content += f"""
## 📊 Report Summary

This comprehensive architecture report was generated by analyzing the multi-agent conversation between {metadata['total_agents']} specialized architecture agents. The report includes {metadata['total_recommendations']} total recommendations across various architectural domains.

### Report Sections:
- **Agent Recommendations Summary**: Overview of each agent's contributions
- **Key Insights**: Critical findings from the conversation
- **Risk Assessment**: Identified risks and challenges
- **Cost Considerations**: Financial implications and optimizations
- **Implementation Roadmap**: Phased approach to implementation
- **Detailed Agent Recommendations**: Comprehensive recommendations from each specialist

### Next Steps:
1. Review all agent recommendations carefully
2. Prioritize recommendations based on business needs
3. Develop detailed implementation plans
4. Consider risk mitigation strategies
5. Plan cost optimization approaches

---
*Report generated by Multi-Agent Architecture Advisory System*
"""
    
    return markdown_content

def main():
    st.set_page_config(
        page_title="Architecture Advisory System", 
        page_icon="🏗️",
        layout="wide"
    )
    
    st.title("🏗️ Multi-Agent Architecture Advisory System")
    st.markdown("*Powered by AutoGen + Anthropic Claude*")
    
    # Sidebar for configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # API Key input
        api_key = st.text_input(
            "Anthropic API Key", 
            type="password", 
            value=os.getenv("ANTHROPIC_API_KEY", "")
        )
        
        if api_key:
            os.environ["ANTHROPIC_API_KEY"] = api_key
        
        st.header("🤖 Available Agents")
        st.markdown("""
        - **Head of Architecture**: Strategic oversight
        - **Cloud Architect**: Cloud solutions expert  
        - **OSS Architect**: Open source specialist
        - **Lead Architect**: General architecture expert
        """)
    
    # Main interface
    if not api_key:
        st.warning("⚠️ Please enter your Anthropic API key in the sidebar to continue.")
        return
    
    # Initialize agents
    if 'agents_system' not in st.session_state:
        with st.spinner("Initializing AI Architecture Team..."):
            st.session_state.agents_system = ArchitectureAgents()
            st.session_state.group_chat_manager, st.session_state.group_chat = st.session_state.agents_system.create_group_chat()
    
    # Input section
    st.header("📝 Architecture Request")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        user_request = st.text_area(
            "Describe your architectural challenge or requirement:",
            placeholder="e.g., I need to design a scalable e-commerce platform that can handle 10k+ concurrent users, with considerations for cloud deployment and open source technologies...",
            height=120
        )
    
    with col2:
        st.markdown("**Request Categories:**")
        categories = st.multiselect(
            "Select relevant areas:",
            ["Cloud Architecture", "Open Source", "Scalability", "Security", "Cost Optimization", "Integration"]
        )
        
        urgency = st.selectbox("Priority Level:", ["Low", "Medium", "High", "Critical"])
    
    # Process request
    if st.button("🚀 Get Architecture Recommendations", type="primary"):
        if not user_request.strip():
            st.error("Please enter an architecture request.")
            return
        
        # Format the request with context
        formatted_request = f"""
        **Architecture Request:** {user_request}
        
        **Categories:** {', '.join(categories) if categories else 'General'}
        **Priority:** {urgency}
        
        Please analyze this request and provide comprehensive architectural recommendations.
        Consider multiple perspectives and ensure all relevant aspects are covered.
        """
        
        # Create conversation
        with st.spinner("🤔 Architecture team is collaborating..."):
            try:
                # Initiate the conversation
                st.session_state.agents_system.agents["user_proxy"].initiate_chat(
                    st.session_state.group_chat_manager,
                    message=formatted_request
                )
                
                # Display results
                st.header("💡 Architecture Recommendations")
                
                # Show conversation history
                messages = st.session_state.group_chat.messages
                
                for i, msg in enumerate(messages):
                    agent_name = msg.get("name", "Unknown")
                    content = msg.get("content", "")
                    
                    # Skip empty messages
                    if not content.strip():
                        continue
                    
                    # Create expandable sections for each agent response
                    with st.expander(f"💬 {agent_name} Response", expanded=(i == len(messages)-1)):
                        st.markdown(content)
                
                # Generate and display comprehensive report
                if messages:
                    st.header("📊 Comprehensive Architecture Report")
                    
                    # Initialize report generator and graph generator
                    report_generator = ArchitectureReportGenerator()
                    graph_generator = DynamicGraphGenerator()
                    
                    # Generate summary table
                    summary_table = report_generator.generate_summary_table(
                        messages, user_request, categories, urgency
                    )
                    
                    # Display summary table
                    st.subheader("📋 Agent Recommendations Summary")
                    st.dataframe(
                        summary_table,
                        use_container_width=True,
                        hide_index=True
                    )
                    
                    # Generate detailed report
                    detailed_report = report_generator.generate_detailed_report(
                        messages, user_request, categories, urgency
                    )
                    
                    # Display detailed report sections
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.subheader("🔍 Key Insights")
                        if detailed_report["key_insights"]:
                            for i, insight in enumerate(detailed_report["key_insights"], 1):
                                st.write(f"{i}. {insight}")
                        else:
                            st.info("No specific insights extracted from the conversation.")
                        
                        st.subheader("⚠️ Risk Assessment")
                        if detailed_report["risk_assessment"]:
                            for i, risk in enumerate(detailed_report["risk_assessment"], 1):
                                st.write(f"{i}. {risk}")
                        else:
                            st.info("No specific risks identified in the conversation.")
                    
                    with col2:
                        st.subheader("💰 Cost Considerations")
                        if detailed_report["cost_considerations"]:
                            for i, cost in enumerate(detailed_report["cost_considerations"], 1):
                                st.write(f"{i}. {cost}")
                        else:
                            st.info("No specific cost considerations mentioned.")
                        
                        st.subheader("📈 Implementation Roadmap")
                        roadmap_df = pd.DataFrame(detailed_report["implementation_roadmap"])
                        st.dataframe(roadmap_df, use_container_width=True, hide_index=True)
                    
                    # Generate and display dynamic graphs
                    st.header("📊 Dynamic Architecture Visualizations")
                    
                    # Extract architecture components
                    components = graph_generator.extract_architecture_components(messages)
                    
                    # Create tabs for different visualizations
                    tab1, tab2 = st.tabs(["📊 Component Distribution", "⏱️ Implementation Timeline"])
                    
                    with tab1:
                        st.subheader("Architecture Components Distribution")
                        distribution_fig = graph_generator.create_component_distribution_chart(components)
                        st.plotly_chart(distribution_fig, use_container_width=True)
                        
                        # Show component details
                        st.subheader("📋 Identified Components")
                        for component_type, component_list in components.items():
                            if component_list:
                                with st.expander(f"{component_type.replace('_', ' ').title()} ({len(component_list)} items)"):
                                    for i, component in enumerate(component_list, 1):
                                        st.write(f"{i}. {component}")
                    
                    with tab2:
                        st.subheader("Implementation Timeline")
                        timeline_fig = graph_generator.create_implementation_timeline(detailed_report)
                        st.plotly_chart(timeline_fig, use_container_width=True)
                    
                    # Export functionality
                    st.subheader("📥 Export Report")
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        # Export summary table as CSV
                        csv_data = summary_table.to_csv(index=False)
                        st.download_button(
                            label="📊 Download Summary Table (CSV)",
                            data=csv_data,
                            file_name=f"architecture_summary_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                            mime="text/csv"
                        )
                    
                    with col2:
                        # Export detailed report as JSON
                        json_data = json.dumps(detailed_report, indent=2)
                        st.download_button(
                            label="📋 Download Detailed Report (JSON)",
                            data=json_data,
                            file_name=f"architecture_report_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                            mime="application/json"
                        )
                    
                    with col3:
                        # Export as Markdown
                        markdown_report = generate_markdown_report(detailed_report, summary_table)
                        st.download_button(
                            label="📄 Download Report (Markdown)",
                            data=markdown_report,
                            file_name=f"architecture_report_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                            mime="text/markdown"
                        )
                    
                    # Display metadata
                    st.subheader("📊 Report Metadata")
                    metadata = detailed_report["metadata"]
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric("Total Agents", metadata["total_agents"])
                    with col2:
                        st.metric("Total Recommendations", metadata["total_recommendations"])
                    with col3:
                        st.metric("Categories", len(metadata["categories"]))
                    with col4:
                        st.metric("Priority", metadata["priority"])
                
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
                st.info("Please check your API key and try again.")
    
    # Additional features
    st.header("🔧 Additional Features")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📊 Architecture Patterns"):
            st.info("Coming soon: Interactive architecture pattern explorer")
    
    with col2:
        if st.button("💾 Save Recommendations"):
            st.info("Coming soon: Export recommendations to PDF/Markdown")
    
    with col3:
        if st.button("🔄 New Session"):
            # Clear session state
            for key in ['agents_system', 'group_chat_manager', 'group_chat']:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()

if __name__ == "__main__":
    main()