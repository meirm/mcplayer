// hooks/useMCP.ts - React integration for MCP
import { useState, useCallback, useEffect } from 'react';
import axios, { AxiosError } from 'axios';

const API_BASE = process.env.REACT_APP_MCPO_URL || 'http://localhost:8003';
const API_KEY = process.env.REACT_APP_MCPO_API_KEY || 'task-management-secret';

export interface MCPTool {
  name: string;
  description: string;
  inputSchema: Record<string, any>;
}

export interface MCPResource {
  uri: string;
  name: string;
  description: string;
  mimeType: string;
}

export interface MCPPrompt {
  name: string;
  description: string;
  arguments: Array<{ name: string; description: string; required: boolean }>;
}

export interface MCPCapabilities {
  tools: MCPTool[];
  resources: MCPResource[];
  prompts: MCPPrompt[];
}

export interface Task {
  id: number;
  title: string;
  description?: string;
  status: 'pending' | 'in_progress' | 'completed' | 'cancelled';
  assignee_id?: number;
  priority: 'low' | 'medium' | 'high' | 'critical';
  due_date?: string;
  created_at: string;
  updated_at: string;
}

export const useMCP = () => {
  const [capabilities, setCapabilities] = useState<MCPCapabilities | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Discover capabilities on mount
  useEffect(() => {
    const discover = async () => {
      try {
        setLoading(true);
        // For MCPO, we get capabilities from the OpenAPI schema
        const { data } = await axios.get(`${API_BASE}/openapi.json`);
        
        // Extract tools from OpenAPI paths
        const tools: MCPTool[] = [];
        if (data.paths) {
          Object.entries(data.paths).forEach(([path, methods]: [string, any]) => {
            const toolName = path.substring(1); // Remove leading slash
            if (methods.post) {
              tools.push({
                name: toolName,
                description: methods.post.summary || methods.post.description || toolName,
                inputSchema: methods.post.requestBody?.content?.['application/json']?.schema || {}
              });
            }
          });
        }
        
        // Set basic capabilities (resources and prompts are accessed differently in MCPO)
        setCapabilities({
          tools,
          resources: [], // MCPO doesn't expose resources directly
          prompts: []    // MCPO doesn't expose prompts directly
        });
        setError(null);
      } catch (err) {
        const axiosError = err as AxiosError;
        setError(axiosError.message || 'Failed to connect to MCPO server');
        console.error('Discovery error:', err);
      } finally {
        setLoading(false);
      }
    };
    
    discover();
  }, []);

  // Execute tool with optional progress support
  const executeTool = useCallback(async (
    toolName: string, 
    args: any,
    onProgress?: (current: number, total: number) => void
  ) => {
    if (onProgress) {
      // Use WebSocket for progress
      return new Promise((resolve, reject) => {
        const wsUrl = API_BASE.replace('http://', 'ws://').replace('/api', '');
        const ws = new WebSocket(`${wsUrl}/ws/tools/${toolName}`);
        
        ws.onopen = () => {
          ws.send(JSON.stringify({ arguments: args }));
        };
        
        ws.onmessage = (event) => {
          const data = JSON.parse(event.data);
          
          switch (data.type) {
            case 'progress':
              onProgress(data.current, data.total);
              break;
            case 'complete':
              resolve(data.result);
              ws.close();
              break;
            case 'error':
              reject(new Error(data.error));
              ws.close();
              break;
          }
        };
        
        ws.onerror = (error) => {
          reject(error);
        };
      });
    } else {
      // Regular HTTP call to MCPO endpoint
      try {
        const { data } = await axios.post(
          `${API_BASE}/${toolName}`, 
          args,
          {
            headers: {
              'Authorization': `Bearer ${API_KEY}`,
              'Content-Type': 'application/json'
            }
          }
        );
        
        // MCPO returns the result directly
        return data;
      } catch (err) {
        const axiosError = err as AxiosError;
        throw new Error(axiosError.message || 'Failed to execute tool');
      }
    }
  }, []);

  // Read resource - for MCPO, we'll use search_tasks to get task lists
  const readResource = useCallback(async (resourcePath: string, params?: any) => {
    try {
      // Map resource paths to appropriate tool calls
      if (resourcePath === 'tasks/list' || resourcePath === 'task/list') {
        // Use search_tasks tool with no filters to get all tasks
        const result = await executeTool('search_tasks', { limit: 100 });
        return result;
      }
      
      throw new Error(`Resource ${resourcePath} not supported with MCPO`);
    } catch (err) {
      const axiosError = err as AxiosError;
      throw new Error(axiosError.message || 'Failed to read resource');
    }
  }, [executeTool]);

  // Get prompt - MCPO doesn't directly expose prompts, so this is a placeholder
  const getPrompt = useCallback(async (promptName: string, args?: any) => {
    try {
      // MCPO doesn't expose prompts directly through REST endpoints
      // This would require a separate implementation or direct MCP client
      throw new Error('Prompts not available through MCPO REST interface');
    } catch (err) {
      const axiosError = err as AxiosError;
      throw new Error(axiosError.message || 'Failed to get prompt');
    }
  }, []);

  return {
    capabilities,
    executeTool,
    readResource,
    getPrompt,
    loading,
    error
  };
};