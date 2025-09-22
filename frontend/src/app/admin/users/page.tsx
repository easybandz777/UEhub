'use client'

import React, { useState, useEffect } from 'react'
import { useAuth, useRole, withAuth } from '@/components/auth/AuthProvider'
import { apiClient, User } from '@/lib/api'
import { 
  Users, 
  Plus, 
  Edit, 
  Trash2, 
  Eye, 
  Search,
  UserPlus,
  Shield,
  Package
} from 'lucide-react'

interface CreateUserForm {
  email: string
  name: string
  password: string
  role: string
  department: string
  phone: string
  notes: string
}

function UserManagementPage() {
  const { user } = useAuth()
  const { canManageUsers, canCreateUsers, canDeleteUsers } = useRole()
  const [users, setUsers] = useState<User[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [searchTerm, setSearchTerm] = useState('')
  const [showCreateForm, setShowCreateForm] = useState(false)
  const [editingUser, setEditingUser] = useState<User | null>(null)
  const [selectedUserId, setSelectedUserId] = useState<string | null>(null)
  const [userInventory, setUserInventory] = useState<any>(null)

  const [createForm, setCreateForm] = useState<CreateUserForm>({
    email: '',
    name: '',
    password: '',
    role: 'employee',
    department: '',
    phone: '',
    notes: ''
  })

  useEffect(() => {
    if (!canManageUsers) {
      setError('You do not have permission to manage users')
      setLoading(false)
      return
    }
    loadUsers()
  }, [canManageUsers])

  const loadUsers = async () => {
    try {
      setLoading(true)
      const response = await apiClient.getAllUsers()
      setUsers(response.users)
      setError(null)
    } catch (err) {
      setError('Failed to load users')
      console.error('Error loading users:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleCreateUser = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      await apiClient.createUser(createForm)
      setShowCreateForm(false)
      setCreateForm({
        email: '',
        name: '',
        password: '',
        role: 'employee',
        department: '',
        phone: '',
        notes: ''
      })
      await loadUsers()
    } catch (err) {
      setError('Failed to create user')
      console.error('Error creating user:', err)
    }
  }

  const handleDeleteUser = async (userId: string) => {
    if (!canDeleteUsers) {
      setError('You do not have permission to delete users')
      return
    }
    
    if (confirm('Are you sure you want to deactivate this user?')) {
      try {
        await apiClient.deleteUser(userId)
        await loadUsers()
      } catch (err) {
        setError('Failed to deactivate user')
        console.error('Error deleting user:', err)
      }
    }
  }

  const handleViewInventory = async (userId: string) => {
    try {
      const inventory = await apiClient.getUserInventory(userId)
      setUserInventory(inventory)
      setSelectedUserId(userId)
    } catch (err) {
      setError('Failed to load user inventory')
      console.error('Error loading inventory:', err)
    }
  }

  const filteredUsers = users.filter(u => 
    u.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    u.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
    u.role.toLowerCase().includes(searchTerm.toLowerCase()) ||
    (u.department && u.department.toLowerCase().includes(searchTerm.toLowerCase()))
  )

  const getRoleBadgeColor = (role: string) => {
    switch (role) {
      case 'superadmin': return 'bg-red-100 text-red-800'
      case 'admin': return 'bg-blue-100 text-blue-800'
      case 'manager': return 'bg-green-100 text-green-800'
      case 'employee': return 'bg-gray-100 text-gray-800'
      case 'worker': return 'bg-yellow-100 text-yellow-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  if (!canManageUsers) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <Shield className="mx-auto h-12 w-12 text-gray-400" />
          <h3 className="mt-2 text-sm font-medium text-gray-900">Access Denied</h3>
          <p className="mt-1 text-sm text-gray-500">
            You do not have permission to access user management.
          </p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 flex items-center">
                <Users className="mr-3 h-8 w-8" />
                User Management
              </h1>
              <p className="mt-2 text-gray-600">
                Manage users, roles, and permissions
              </p>
            </div>
            {canCreateUsers && (
              <button
                onClick={() => setShowCreateForm(true)}
                className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 flex items-center"
              >
                <UserPlus className="mr-2 h-4 w-4" />
                Add User
              </button>
            )}
          </div>
        </div>

        {error && (
          <div className="mb-6 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
            {error}
          </div>
        )}

        {/* Search */}
        <div className="mb-6">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
            <input
              type="text"
              placeholder="Search users..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10 pr-4 py-2 border border-gray-300 rounded-lg w-full max-w-md"
            />
          </div>
        </div>

        {/* Users Table */}
        <div className="bg-white shadow rounded-lg overflow-hidden">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  User
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Role
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Department
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {loading ? (
                <tr>
                  <td colSpan={5} className="px-6 py-4 text-center text-gray-500">
                    Loading users...
                  </td>
                </tr>
              ) : filteredUsers.length === 0 ? (
                <tr>
                  <td colSpan={5} className="px-6 py-4 text-center text-gray-500">
                    No users found
                  </td>
                </tr>
              ) : (
                filteredUsers.map((u) => (
                  <tr key={u.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div>
                        <div className="text-sm font-medium text-gray-900">{u.name}</div>
                        <div className="text-sm text-gray-500">{u.email}</div>
                        {u.phone && (
                          <div className="text-xs text-gray-400">{u.phone}</div>
                        )}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getRoleBadgeColor(u.role)}`}>
                        {u.role}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {u.department || '-'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                        u.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                      }`}>
                        {u.is_active ? 'Active' : 'Inactive'}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                      <div className="flex space-x-2">
                        <button
                          onClick={() => handleViewInventory(u.id)}
                          className="text-blue-600 hover:text-blue-900"
                          title="View Inventory"
                        >
                          <Package className="h-4 w-4" />
                        </button>
                        <button
                          onClick={() => setEditingUser(u)}
                          className="text-indigo-600 hover:text-indigo-900"
                          title="Edit User"
                        >
                          <Edit className="h-4 w-4" />
                        </button>
                        {canDeleteUsers && u.id !== user?.id && (
                          <button
                            onClick={() => handleDeleteUser(u.id)}
                            className="text-red-600 hover:text-red-900"
                            title="Deactivate User"
                          >
                            <Trash2 className="h-4 w-4" />
                          </button>
                        )}
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        {/* Create User Modal */}
        {showCreateForm && (
          <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
            <div className="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
              <h3 className="text-lg font-bold text-gray-900 mb-4">Create New User</h3>
              <form onSubmit={handleCreateUser}>
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Email</label>
                    <input
                      type="email"
                      required
                      value={createForm.email}
                      onChange={(e) => setCreateForm({...createForm, email: e.target.value})}
                      className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Name</label>
                    <input
                      type="text"
                      required
                      value={createForm.name}
                      onChange={(e) => setCreateForm({...createForm, name: e.target.value})}
                      className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Password</label>
                    <input
                      type="password"
                      required
                      value={createForm.password}
                      onChange={(e) => setCreateForm({...createForm, password: e.target.value})}
                      className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Role</label>
                    <select
                      value={createForm.role}
                      onChange={(e) => setCreateForm({...createForm, role: e.target.value})}
                      className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2"
                    >
                      <option value="employee">Employee</option>
                      <option value="worker">Worker</option>
                      <option value="manager">Manager</option>
                      <option value="admin">Admin</option>
                      <option value="superadmin">Super Admin</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Department</label>
                    <input
                      type="text"
                      value={createForm.department}
                      onChange={(e) => setCreateForm({...createForm, department: e.target.value})}
                      className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2"
                    />
                  </div>
                </div>
                <div className="flex justify-end space-x-3 mt-6">
                  <button
                    type="button"
                    onClick={() => setShowCreateForm(false)}
                    className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-200 rounded-md hover:bg-gray-300"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    className="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700"
                  >
                    Create User
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}

        {/* User Inventory Modal */}
        {userInventory && (
          <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
            <div className="relative top-20 mx-auto p-5 border w-2/3 max-w-4xl shadow-lg rounded-md bg-white">
              <div className="flex justify-between items-center mb-4">
                <h3 className="text-lg font-bold text-gray-900">
                  {userInventory.user.name}'s Inventory
                </h3>
                <button
                  onClick={() => {setUserInventory(null); setSelectedUserId(null)}}
                  className="text-gray-400 hover:text-gray-600"
                >
                  ✕
                </button>
              </div>
              <div className="mb-4">
                <p className="text-sm text-gray-600">{userInventory.user.email}</p>
                <p className="text-sm text-gray-500">
                  {userInventory.inventory.total} items
                </p>
              </div>
              <div className="max-h-96 overflow-y-auto">
                {userInventory.inventory.items.length === 0 ? (
                  <p className="text-center text-gray-500 py-8">No inventory items found</p>
                ) : (
                  <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">SKU</th>
                        <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Name</th>
                        <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Location</th>
                        <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Qty</th>
                        <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                      </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                      {userInventory.inventory.items.map((item: any) => (
                        <tr key={item.id}>
                          <td className="px-4 py-2 text-sm font-medium text-gray-900">{item.sku}</td>
                          <td className="px-4 py-2 text-sm text-gray-900">{item.name}</td>
                          <td className="px-4 py-2 text-sm text-gray-900">{item.location}</td>
                          <td className="px-4 py-2 text-sm text-gray-900">{item.qty}</td>
                          <td className="px-4 py-2 text-sm">
                            <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                              item.is_low_stock ? 'bg-red-100 text-red-800' : 'bg-green-100 text-green-800'
                            }`}>
                              {item.is_low_stock ? 'Low Stock' : 'In Stock'}
                            </span>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                )}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default withAuth(UserManagementPage)
