'use client';

import { useEffect, useState, useCallback } from 'react';
import { Todo } from '@/types';
import { fetchTodos, createTodo, updateTodo, deleteTodo, toggleTodoComplete } from '@/lib/api';
import TodoForm from '@/components/todos/TodoForm';
import TodoList from '@/components/todos/TodoList';
import Link from 'next/link';

export default function TodosPage() {
  const [todos, setTodos] = useState<Todo[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');

  const loadTodos = useCallback(async () => {
    try {
      const data = await fetchTodos();
      setTodos(data);
      setError('');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load todos');
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    loadTodos();
  }, [loadTodos]);

  const handleCreate = async (title: string) => {
    const newTodo = await createTodo({ title });
    setTodos((prev) => [newTodo, ...prev]);
  };

  const handleToggle = async (id: string, completed: boolean) => {
    const updatedTodo = await toggleTodoComplete(id, completed);
    setTodos((prev) =>
      prev.map((todo) => (todo.id === id ? updatedTodo : todo))
    );
  };

  const handleUpdate = async (id: string, title: string) => {
    const updatedTodo = await updateTodo(id, { title });
    setTodos((prev) =>
      prev.map((todo) => (todo.id === id ? updatedTodo : todo))
    );
  };

  const handleDelete = async (id: string) => {
    await deleteTodo(id);
    setTodos((prev) => prev.filter((todo) => todo.id !== id));
  };

  const completedCount = todos.filter((t) => t.completed).length;
  const pendingCount = todos.length - completedCount;

  return (
    <div className="max-w-3xl mx-auto">
      {/* Header Card */}
      <div className="bg-white rounded-3xl shadow-xl p-8 mb-6 border border-gray-100">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-4">
            <div className="w-14 h-14 bg-gradient-to-br from-purple-500 via-pink-500 to-blue-500 rounded-2xl flex items-center justify-center shadow-lg">
              <span className="text-3xl">📋</span>
            </div>
            <div>
              <h1 className="text-2xl font-bold bg-gradient-to-r from-purple-600 via-pink-600 to-blue-600 bg-clip-text text-transparent">
                My Todos
              </h1>
              <p className="text-sm text-gray-500">Manage your tasks manually</p>
            </div>
          </div>

          {/* AI Chat Promo */}
          <Link
            href="/chat"
            className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-purple-100 to-pink-100 rounded-xl text-purple-700 text-sm font-medium hover:from-purple-200 hover:to-pink-200 transition-all"
          >
            <span>✨</span>
            Try AI Chat
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" className="w-4 h-4">
              <path fillRule="evenodd" d="M5 10a.75.75 0 0 1 .75-.75h6.638L10.23 7.29a.75.75 0 1 1 1.04-1.08l3.5 3.25a.75.75 0 0 1 0 1.08l-3.5 3.25a.75.75 0 1 1-1.04-1.08l2.158-1.96H5.75A.75.75 0 0 1 5 10Z" clipRule="evenodd" />
            </svg>
          </Link>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-3 gap-4 mb-6">
          <div className="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-2xl p-4 border border-blue-100">
            <div className="text-3xl font-bold text-blue-600">{todos.length}</div>
            <div className="text-sm text-blue-600/70">Total Tasks</div>
          </div>
          <div className="bg-gradient-to-br from-amber-50 to-orange-50 rounded-2xl p-4 border border-amber-100">
            <div className="text-3xl font-bold text-amber-600">{pendingCount}</div>
            <div className="text-sm text-amber-600/70">Pending</div>
          </div>
          <div className="bg-gradient-to-br from-green-50 to-emerald-50 rounded-2xl p-4 border border-green-100">
            <div className="text-3xl font-bold text-green-600">{completedCount}</div>
            <div className="text-sm text-green-600/70">Completed</div>
          </div>
        </div>

        {/* Add Todo Form */}
        <TodoForm onSubmit={handleCreate} />
      </div>

      {/* Error Message */}
      {error && (
        <div className="mb-6 p-4 bg-gradient-to-r from-red-50 to-pink-50 border border-red-200 rounded-2xl text-red-700 flex items-center gap-3">
          <span className="text-xl">⚠️</span>
          <span>{error}</span>
          <button
            onClick={() => setError('')}
            className="ml-auto text-red-400 hover:text-red-600"
          >
            ✕
          </button>
        </div>
      )}

      {/* Todo List */}
      <div className="bg-white rounded-3xl shadow-xl p-6 border border-gray-100">
        <TodoList
          todos={todos}
          isLoading={isLoading}
          onToggle={handleToggle}
          onUpdate={handleUpdate}
          onDelete={handleDelete}
        />
      </div>

      {/* Progress Bar */}
      {todos.length > 0 && (
        <div className="mt-6 bg-white rounded-2xl shadow-lg p-4 border border-gray-100">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-gray-700">Progress</span>
            <span className="text-sm font-bold bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent">
              {Math.round((completedCount / todos.length) * 100)}%
            </span>
          </div>
          <div className="h-3 bg-gray-100 rounded-full overflow-hidden">
            <div
              className="h-full bg-gradient-to-r from-purple-500 via-pink-500 to-blue-500 rounded-full transition-all duration-500"
              style={{ width: `${(completedCount / todos.length) * 100}%` }}
            />
          </div>
          <p className="text-xs text-gray-500 mt-2 text-center">
            {completedCount} of {todos.length} tasks completed
          </p>
        </div>
      )}
    </div>
  );
}
