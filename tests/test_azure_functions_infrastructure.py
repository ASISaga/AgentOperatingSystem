"""
Tests for GenesisAgents and MCPServers infrastructure
"""

import pytest
import json
import os

# Import schemas directly from their modules
# Note: The azure_functions directory is in the parent directory of tests
GENESIS_AGENTS_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../azure_functions/GenesisAgents'))
MCP_SERVERS_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../azure_functions/MCPServers'))

# Import agent config schema
import importlib.util
spec = importlib.util.spec_from_file_location("agent_config_schema", os.path.join(GENESIS_AGENTS_PATH, "agent_config_schema.py"))
agent_config_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(agent_config_module)

AgentConfiguration = agent_config_module.AgentConfiguration
AgentRegistry = agent_config_module.AgentRegistry
AgentType = agent_config_module.AgentType
DomainKnowledge = agent_config_module.DomainKnowledge
MCPToolReference = agent_config_module.MCPToolReference

# Import MCP server schema
spec = importlib.util.spec_from_file_location("mcp_server_schema", os.path.join(MCP_SERVERS_PATH, "mcp_server_schema.py"))
mcp_server_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mcp_server_module)

MCPServerConfiguration = mcp_server_module.MCPServerConfiguration
MCPServerRegistry = mcp_server_module.MCPServerRegistry
MCPServerType = mcp_server_module.MCPServerType
MCPToolDefinition = mcp_server_module.MCPToolDefinition


class TestAgentConfigurationSchema:
    """Test agent configuration schema and validation"""
    
    def test_agent_configuration_valid(self):
        """Test valid agent configuration"""
        config = AgentConfiguration(
            agent_id="test_agent",
            agent_type=AgentType.PURPOSE_DRIVEN,
            purpose="Test purpose",
            domain_knowledge=DomainKnowledge(
                domain="test",
                training_data_path="test/path.jsonl"
            )
        )
        assert config.agent_id == "test_agent"
        assert config.purpose == "Test purpose"
        assert config.enabled is True
    
    def test_agent_configuration_with_tools(self):
        """Test agent configuration with MCP tools"""
        config = AgentConfiguration(
            agent_id="test_agent",
            purpose="Test purpose",
            domain_knowledge=DomainKnowledge(
                domain="test",
                training_data_path="test/path.jsonl"
            ),
            mcp_tools=[
                MCPToolReference(
                    server_name="github",
                    tool_name="create_issue"
                )
            ]
        )
        assert len(config.mcp_tools) == 1
        assert config.mcp_tools[0].server_name == "github"
    
    def test_agent_registry_loading(self):
        """Test loading agent registry from JSON"""
        registry_path = os.path.join(
            os.path.dirname(__file__),
            '../azure_functions/GenesisAgents/example_agent_registry.json'
        )
        
        with open(registry_path) as f:
            registry_data = json.load(f)
        
        registry = AgentRegistry(**registry_data)
        assert len(registry.agents) > 0
        
        # Check all agents are valid
        for agent in registry.agents:
            assert agent.agent_id
            assert agent.purpose
            assert agent.domain_knowledge
    
    def test_agent_registry_enabled_filter(self):
        """Test filtering enabled agents"""
        registry = AgentRegistry(
            agents=[
                AgentConfiguration(
                    agent_id="agent1",
                    purpose="Purpose 1",
                    domain_knowledge=DomainKnowledge(
                        domain="test",
                        training_data_path="path1.jsonl"
                    ),
                    enabled=True
                ),
                AgentConfiguration(
                    agent_id="agent2",
                    purpose="Purpose 2",
                    domain_knowledge=DomainKnowledge(
                        domain="test",
                        training_data_path="path2.jsonl"
                    ),
                    enabled=False
                )
            ]
        )
        
        enabled = registry.get_enabled_agents()
        assert len(enabled) == 1
        assert enabled[0].agent_id == "agent1"
    
    def test_agent_registry_get_by_id(self):
        """Test getting agent by ID"""
        registry = AgentRegistry(
            agents=[
                AgentConfiguration(
                    agent_id="agent1",
                    purpose="Purpose 1",
                    domain_knowledge=DomainKnowledge(
                        domain="test",
                        training_data_path="path1.jsonl"
                    )
                )
            ]
        )
        
        agent = registry.get_agent_by_id("agent1")
        assert agent is not None
        assert agent.agent_id == "agent1"
        
        not_found = registry.get_agent_by_id("nonexistent")
        assert not_found is None


class TestMCPServerConfigurationSchema:
    """Test MCP server configuration schema and validation"""
    
    def test_mcp_server_configuration_valid(self):
        """Test valid MCP server configuration"""
        config = MCPServerConfiguration(
            server_id="test_server",
            server_name="Test Server",
            server_type=MCPServerType.STDIO,
            command="python",
            args=["-m", "test_server"]
        )
        assert config.server_id == "test_server"
        assert config.enabled is True
        assert config.auto_start is True
    
    def test_mcp_server_configuration_with_tools(self):
        """Test MCP server configuration with tools"""
        config = MCPServerConfiguration(
            server_id="test_server",
            server_name="Test Server",
            server_type=MCPServerType.STDIO,
            command="python",
            tools=[
                MCPToolDefinition(
                    name="test_tool",
                    description="Test tool",
                    input_schema={
                        "type": "object",
                        "properties": {
                            "param1": {"type": "string"}
                        }
                    }
                )
            ]
        )
        assert len(config.tools) == 1
        assert config.tools[0].name == "test_tool"
    
    def test_mcp_server_registry_loading(self):
        """Test loading MCP server registry from JSON"""
        registry_path = os.path.join(
            os.path.dirname(__file__),
            '../azure_functions/MCPServers/example_mcp_server_registry.json'
        )
        
        with open(registry_path) as f:
            registry_data = json.load(f)
        
        registry = MCPServerRegistry(**registry_data)
        assert len(registry.servers) > 0
        
        # Check all servers are valid
        for server in registry.servers:
            assert server.server_id
            assert server.server_name
            assert server.command
    
    def test_mcp_server_registry_auto_start_filter(self):
        """Test filtering auto-start servers"""
        registry = MCPServerRegistry(
            servers=[
                MCPServerConfiguration(
                    server_id="server1",
                    server_name="Server 1",
                    command="cmd1",
                    enabled=True,
                    auto_start=True
                ),
                MCPServerConfiguration(
                    server_id="server2",
                    server_name="Server 2",
                    command="cmd2",
                    enabled=True,
                    auto_start=False
                ),
                MCPServerConfiguration(
                    server_id="server3",
                    server_name="Server 3",
                    command="cmd3",
                    enabled=False,
                    auto_start=True
                )
            ]
        )
        
        auto_start = registry.get_auto_start_servers()
        assert len(auto_start) == 1
        assert auto_start[0].server_id == "server1"
    
    def test_mcp_server_registry_get_by_id(self):
        """Test getting server by ID"""
        registry = MCPServerRegistry(
            servers=[
                MCPServerConfiguration(
                    server_id="server1",
                    server_name="Server 1",
                    command="cmd1"
                )
            ]
        )
        
        server = registry.get_server_by_id("server1")
        assert server is not None
        assert server.server_id == "server1"
        
        not_found = registry.get_server_by_id("nonexistent")
        assert not_found is None


class TestIntegration:
    """Test integration between agent and MCP server configurations"""
    
    def test_agent_mcp_tool_references(self):
        """Test that agent MCP tool references match available servers"""
        # Load both registries
        agent_registry_path = os.path.join(
            os.path.dirname(__file__),
            '../azure_functions/GenesisAgents/example_agent_registry.json'
        )
        mcp_registry_path = os.path.join(
            os.path.dirname(__file__),
            '../azure_functions/MCPServers/example_mcp_server_registry.json'
        )
        
        with open(agent_registry_path) as f:
            agent_data = json.load(f)
        with open(mcp_registry_path) as f:
            mcp_data = json.load(f)
        
        agent_registry = AgentRegistry(**agent_data)
        mcp_registry = MCPServerRegistry(**mcp_data)
        
        # Get all server IDs
        available_servers = {server.server_id for server in mcp_registry.servers}
        
        # Check all agent tool references point to available servers
        for agent in agent_registry.agents:
            for tool_ref in agent.mcp_tools:
                assert tool_ref.server_name in available_servers, \
                    f"Agent {agent.agent_id} references unknown server {tool_ref.server_name}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
