import React, { useState, useEffect } from 'react';
import { useMCP, Task } from '../hooks/useMCP';
import './TaskManager.css';

export const TaskManager: React.FC = () => {
  const { executeTool, readResource, capabilities, loading: mcpLoading, error: mcpError } = useMCP();
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [creating, setCreating] = useState(false);
  const [selectedTasks, setSelectedTasks] = useState<number[]>([]);
  
  // Form state for new task
  const [newTask, setNewTask] = useState({
    title: '',
    description: '',
    priority: 'medium' as const,
    assignee_id: undefined as number | undefined
  });

  // Load tasks on mount and after operations
  const loadTasks = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await readResource('tasks/list');
      // Handle MCPO response format
      if (data.success && data.tasks) {
        setTasks(data.tasks);
      } else if (Array.isArray(data.tasks)) {
        setTasks(data.tasks);
      } else if (Array.isArray(data)) {
        setTasks(data);
      } else {
        setTasks([]);
      }
    } catch (err: any) {
      setError(err.message || 'Failed to load tasks');
      console.error('Load tasks error:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (capabilities) {
      loadTasks();
    }
  }, [capabilities]);

  // Create a new task
  const createTask = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newTask.title.trim()) return;
    
    setCreating(true);
    setError(null);
    try {
      const result = await executeTool('create_task', {
        ...newTask,
        assignee_id: newTask.assignee_id || undefined
      });
      
      // Handle MCPO response format
      if (result.success || result.task) {
        await loadTasks();
        // Reset form
        setNewTask({
          title: '',
          description: '',
          priority: 'medium',
          assignee_id: undefined
        });
      } else {
        setError(result.message || result.error || 'Failed to create task');
      }
    } catch (err: any) {
      setError(err.message || 'Failed to create task');
    } finally {
      setCreating(false);
    }
  };

  // Update task status
  const updateTaskStatus = async (taskId: number, status: Task['status']) => {
    setError(null);
    try {
      const result = await executeTool('update_task', {
        task_id: taskId,
        status
      });
      
      // Handle MCPO response format
      if (result.success || result.task) {
        await loadTasks();
      } else {
        setError(result.message || result.error || 'Failed to update task');
      }
    } catch (err: any) {
      setError(err.message || 'Failed to update task');
    }
  };

  // Bulk update selected tasks
  const bulkUpdateStatus = async (status: Task['status']) => {
    if (selectedTasks.length === 0) return;
    
    setError(null);
    try {
      const result = await executeTool(
        'bulk_update_tasks',
        {
          task_ids: selectedTasks,
          status
        },
        (current, total) => {
          console.log(`Progress: ${current}/${total}`);
        }
      );
      
      // Handle MCPO bulk update response format
      if (result.success || result.succeeded > 0 || result.result?.succeeded > 0) {
        setSelectedTasks([]);
        await loadTasks();
      }
    } catch (err: any) {
      setError(err.message || 'Failed to update tasks');
    }
  };

  // Delete a task
  const deleteTask = async (taskId: number) => {
    if (!window.confirm('Are you sure you want to delete this task?')) return;
    
    setError(null);
    try {
      const result = await executeTool('delete_task', { task_id: taskId });
      
      // Handle MCPO delete response format  
      if (result.success || result.message) {
        await loadTasks();
      } else {
        setError(result.message || result.error || 'Failed to delete task');
      }
    } catch (err: any) {
      setError(err.message || 'Failed to delete task');
    }
  };

  // Toggle task selection
  const toggleTaskSelection = (taskId: number) => {
    setSelectedTasks(prev => 
      prev.includes(taskId) 
        ? prev.filter(id => id !== taskId)
        : [...prev, taskId]
    );
  };

  // Get priority color
  const getPriorityColor = (priority: Task['priority']) => {
    switch (priority) {
      case 'critical': return '#ff4444';
      case 'high': return '#ff8800';
      case 'medium': return '#ffbb33';
      case 'low': return '#99cc00';
      default: return '#33b5e5';
    }
  };

  // Get status color
  const getStatusColor = (status: Task['status']) => {
    switch (status) {
      case 'completed': return '#00c851';
      case 'in_progress': return '#33b5e5';
      case 'cancelled': return '#ff4444';
      default: return '#aa66cc';
    }
  };

  if (mcpLoading) {
    return <div className="loading">Connecting to MCP server...</div>;
  }

  if (mcpError) {
    return <div className="error">Connection Error: {mcpError}</div>;
  }

  return (
    <div className="task-manager">
      <header className="header">
        <h1>Task Management System</h1>
        <p className="subtitle">Powered by Model Context Protocol</p>
      </header>

      {error && (
        <div className="error-banner">
          {error}
          <button onClick={() => setError(null)}>×</button>
        </div>
      )}

      <div className="main-content">
        {/* Create Task Form */}
        <div className="create-task-section">
          <h2>Create New Task</h2>
          <form onSubmit={createTask} className="task-form">
            <input
              type="text"
              placeholder="Task title"
              value={newTask.title}
              onChange={(e) => setNewTask({ ...newTask, title: e.target.value })}
              required
              disabled={creating}
            />
            
            <textarea
              placeholder="Description (optional)"
              value={newTask.description}
              onChange={(e) => setNewTask({ ...newTask, description: e.target.value })}
              disabled={creating}
              rows={3}
            />
            
            <div className="form-row">
              <select
                value={newTask.priority}
                onChange={(e) => setNewTask({ ...newTask, priority: e.target.value as any })}
                disabled={creating}
              >
                <option value="low">Low Priority</option>
                <option value="medium">Medium Priority</option>
                <option value="high">High Priority</option>
                <option value="critical">Critical Priority</option>
              </select>
              
              <input
                type="number"
                placeholder="Assignee ID (optional)"
                value={newTask.assignee_id || ''}
                onChange={(e) => setNewTask({ 
                  ...newTask, 
                  assignee_id: e.target.value ? parseInt(e.target.value) : undefined 
                })}
                disabled={creating}
              />
              
              <button type="submit" disabled={creating || !newTask.title.trim()}>
                {creating ? 'Creating...' : 'Create Task'}
              </button>
            </div>
          </form>
        </div>

        {/* Bulk Actions */}
        {selectedTasks.length > 0 && (
          <div className="bulk-actions">
            <span>{selectedTasks.length} task(s) selected</span>
            <button onClick={() => bulkUpdateStatus('in_progress')}>
              Mark In Progress
            </button>
            <button onClick={() => bulkUpdateStatus('completed')}>
              Mark Completed
            </button>
            <button onClick={() => bulkUpdateStatus('cancelled')}>
              Mark Cancelled
            </button>
            <button onClick={() => setSelectedTasks([])}>
              Clear Selection
            </button>
          </div>
        )}

        {/* Task List */}
        <div className="task-list-section">
          <div className="section-header">
            <h2>Tasks</h2>
            <button onClick={loadTasks} disabled={loading}>
              {loading ? 'Loading...' : 'Refresh'}
            </button>
          </div>

          {loading && tasks.length === 0 ? (
            <div className="loading">Loading tasks...</div>
          ) : tasks.length === 0 ? (
            <div className="empty-state">No tasks found. Create your first task above!</div>
          ) : (
            <div className="task-list">
              {tasks.map(task => (
                <div key={task.id} className="task-card">
                  <div className="task-header">
                    <input
                      type="checkbox"
                      checked={selectedTasks.includes(task.id)}
                      onChange={() => toggleTaskSelection(task.id)}
                    />
                    <h3>{task.title}</h3>
                    <span 
                      className="priority-badge" 
                      style={{ backgroundColor: getPriorityColor(task.priority) }}
                    >
                      {task.priority}
                    </span>
                  </div>
                  
                  {task.description && (
                    <p className="task-description">{task.description}</p>
                  )}
                  
                  <div className="task-meta">
                    <span 
                      className="status-badge"
                      style={{ backgroundColor: getStatusColor(task.status) }}
                    >
                      {task.status.replace('_', ' ')}
                    </span>
                    
                    {task.assignee_id && (
                      <span className="assignee">Assignee: #{task.assignee_id}</span>
                    )}
                    
                    <span className="task-id">ID: {task.id}</span>
                  </div>
                  
                  <div className="task-actions">
                    <select 
                      value={task.status}
                      onChange={(e) => updateTaskStatus(task.id, e.target.value as Task['status'])}
                      className="status-select"
                    >
                      <option value="pending">Pending</option>
                      <option value="in_progress">In Progress</option>
                      <option value="completed">Completed</option>
                      <option value="cancelled">Cancelled</option>
                    </select>
                    
                    <button 
                      onClick={() => deleteTask(task.id)}
                      className="delete-button"
                    >
                      Delete
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Server Capabilities */}
      {capabilities && (
        <div className="capabilities-section">
          <h3>MCP Server Capabilities</h3>
          <div className="capabilities-grid">
            <div className="capability">
              <strong>Tools:</strong> {capabilities.tools.length}
            </div>
            <div className="capability">
              <strong>Resources:</strong> {capabilities.resources.length}
            </div>
            <div className="capability">
              <strong>Prompts:</strong> {capabilities.prompts.length}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};