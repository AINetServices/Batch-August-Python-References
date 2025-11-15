import { useState, useEffect } from 'react';
import { BarChart3, TrendingUp, Users, FileText, Activity } from 'lucide-react';

// Recharts Imports - Added BarChart, PieChart, Cell, AreaChart
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  BarChart, Bar, PieChart, Pie, Cell, AreaChart, Area
} from 'recharts';

// --- 1. NEW DATASETS FOR NEW CHARTS ---

// Data for Horizontal Bar Chart (e.g., Processing Time by Department)
const barChartData = [
  { department: 'HR', time: 1.5 },
  { department: 'Sales', time: 2.1 },
  { department: 'Tech', time: 0.9 },
  { department: 'Legal', time: 3.5 },
  { department: 'Ops', time: 1.8 },
];

// Data for Pie Chart (e.g., Application Status Distribution)
const pieChartData = [
  { name: 'Completed', value: 450 },
  { name: 'Pending', value: 300 },
  { name: 'Rejected', value: 250 },
];
const PIE_COLORS = ['#3b82f6', '#10b981', '#f87171']; // blue, green, red

// Data for Area Chart (e.g., Total System Activity)
const areaChartData = [
    { name: 'Wk 1', activity: 30 },
    { name: 'Wk 2', activity: 45 },
    { name: 'Wk 3', activity: 60 },
    { name: 'Wk 4', activity: 75 },
    { name: 'Wk 5', activity: 90 },
];

// Data for Line Chart (from previous version)
const lineChartData = [
    { name: 'Jan', applications: 400, references: 240 },
    { name: 'Feb', applications: 300, references: 139 },
    { name: 'Mar', applications: 600, references: 980 },
    { name: 'Apr', applications: 500, references: 390 },
    { name: 'May', applications: 780, references: 480 },
    { name: 'Jun', applications: 800, references: 380 },
    { name: 'Jul', applications: 900, references: 430 },
];

// --- 2. NEW CHART COMPONENTS FOR SIMPLICITY ---

// Horizontal Bar Chart (Sideway Columns)
const HorizontalBarChart = () => (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 h-full">
        <h2 className="text-lg font-bold text-gray-900 mb-4">Avg. Time by Department (Days)</h2>
        <ResponsiveContainer width="100%" height={250}>
            {/* Note: layout="vertical" makes it a sideways column chart */}
            <BarChart data={barChartData} layout="vertical" margin={{ top: 5, right: 20, left: 20, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis type="number" stroke="#6b7280" />
                <YAxis dataKey="department" type="category" stroke="#6b7280" width={80} />
                <Tooltip />
                <Bar dataKey="time" fill="#10b981" name="Avg. Time (Days)" />
            </BarChart>
        </ResponsiveContainer>
    </div>
);

// Pie Chart (Simple Distribution)
const StatusPieChart = () => (

    <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 h-full">
        <h2 className="text-lg font-bold text-gray-900 mb-4">Application Status Distribution</h2>
        <ResponsiveContainer width="100%" height={250}>
            <PieChart>
                <Pie
                    data={pieChartData}
                    dataKey="value"
                    nameKey="name"
                    cx="50%"
                    cy="50%"
                    outerRadius={100}
                    labelLine={false}
                    label={({ name, percent }) => `${name} (${((percent ?? 0) * 100).toFixed(0)}%)`}
                >
                    {pieChartData.map((_entry, index) => (
                        <Cell key={`cell-${index}`} fill={PIE_COLORS[index % PIE_COLORS.length]} />
                    ))}
                </Pie>
                <Tooltip />
            </PieChart>
        </ResponsiveContainer>
    </div>
);

// Area Chart (System Activity)
const SystemActivityAreaChart = () => (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 h-full">
        <h2 className="text-lg font-bold text-gray-900 mb-4">Weekly System Activity (Count)</h2>
        <ResponsiveContainer width="100%" height={250}>
            <AreaChart data={areaChartData} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" stroke="#6b7280" />
                <YAxis stroke="#6b7280" />
                <Tooltip />
                <Area type="monotone" dataKey="activity" stroke="#f97316" fill="#fed7aa" name="Total Activity" />
            </AreaChart>
        </ResponsiveContainer>
    </div>
);

// Line Chart (from previous version)
const TrendLineChart = () => (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 h-full">
        <h2 className="text-lg font-bold text-gray-900 mb-4">Applications & References Trend</h2>
        <ResponsiveContainer width="100%" height={250}>
            <LineChart
                data={lineChartData}
                margin={{ top: 5, right: 20, left: 10, bottom: 5 }}
            >
                <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" />
                <XAxis dataKey="name" stroke="#6b7280" />
                <YAxis stroke="#6b7280" />
                <Tooltip />
                <Line type="monotone" dataKey="applications" stroke="#3b82f6" strokeWidth={2} dot={{ r: 4 }} activeDot={{ r: 8 }} name="Total Applications" />
                <Line type="monotone" dataKey="references" stroke="#10b981" strokeWidth={2} dot={{ r: 4 }} activeDot={{ r: 8 }} name="Active References" />
            </LineChart>
        </ResponsiveContainer>
    </div>
);


// --- 3. MAIN COMPONENT (LAYOUT) ---

export function AnalyticsDashboard() {
  const [loading, setLoading] = useState(true);
  
  // Simulate loading for demo
  useEffect(() => {
    const timer = setTimeout(() => setLoading(false), 1500);
    return () => clearTimeout(timer);
  }, []);

  // Sample metrics - kept the original metrics data
  const metrics = [
    { title: 'Total Applications', value: '1,234', change: '+12.5%', trend: 'up', icon: FileText, color: 'blue' },
    { title: 'Active References', value: '3,421', change: '+8.2%', trend: 'up', icon: Users, color: 'green' },
    { title: 'Response Rate', value: '87.3%', change: '+3.1%', trend: 'up', icon: TrendingUp, color: 'purple' },
    { title: 'Avg. Processing Time', value: '2.4 days', change: '-15%', trend: 'down', icon: Activity, color: 'indigo' }
  ];

  const getColorClasses = (color: string) => {
    const colors = {
      blue: 'bg-blue-100 text-blue-600',
      green: 'bg-green-100 text-green-600',
      purple: 'bg-purple-100 text-purple-600',
      indigo: 'bg-indigo-100 text-indigo-600'
    };
    return colors[color as keyof typeof colors] || colors.blue;
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Key Metrics - Unchanged */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {metrics.map((metric, index) => {
            const Icon = metric.icon;
            return (
              <div key={index} className="bg-white rounded-xl shadow-sm p-6 border border-gray-100 hover:shadow-md transition-shadow">
                <div className="flex items-center justify-between mb-4">
                  <div className={`p-3 rounded-lg ${getColorClasses(metric.color)}`}>
                    <Icon className="h-6 w-6" />
                  </div>
                  <div className={`text-sm font-medium ${metric.trend === 'up' ? 'text-green-600' : 'text-red-600'}`}>
                    {metric.change}
                  </div>
                </div>
                <h3 className="text-sm font-medium text-gray-600 mb-1">{metric.title}</h3>
                <p className="text-2xl font-bold text-gray-900">{metric.value}</p>
              </div>
            );
          })}
        </div>

        {/* 4. NEW 2x2 CHART GRID */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
            <TrendLineChart />
            <HorizontalBarChart />
            <StatusPieChart />
            <SystemActivityAreaChart />
        </div>

        {/* The Quick Actions and Recent Activity cards have been removed for a cleaner, chart-focused dashboard, 
            but you can re-introduce them if you need more layout variety: */}
        
             {/* Additional Info Cards (Unchanged) */}
             <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-8">
          {/* ... Quick Actions and Recent Activity cards remain here ... */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <h3 className="text-lg font-bold text-gray-900 mb-4">Quick Actions</h3>
            <div className="space-y-3">
              <button className="w-full text-left px-4 py-3 bg-gray-50 hover:bg-gray-100 rounded-lg transition-colors flex items-center justify-between">
                <span className="text-gray-700">Export Dashboard Data</span>
                <span className="text-blue-600">→</span>
              </button>
              <button className="w-full text-left px-4 py-3 bg-gray-50 hover:bg-gray-100 rounded-lg transition-colors flex items-center justify-between">
                <span className="text-gray-700">Schedule Reports</span>
                <span className="text-blue-600">→</span>
              </button>
              <button className="w-full text-left px-4 py-3 bg-gray-50 hover:bg-gray-100 rounded-lg transition-colors flex items-center justify-between">
                <span className="text-gray-700">Configure Alerts</span>
                <span className="text-blue-600">→</span>
              </button>
            </div>
          </div>

          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <h3 className="text-lg font-bold text-gray-900 mb-4">Recent Activity</h3>
            <div className="space-y-3">
              <div className="flex items-center space-x-3 pb-3 border-b border-gray-100">
                <div className="h-8 w-8 bg-green-100 rounded-full flex items-center justify-center">
                  <Users className="h-4 w-4 text-green-600" />
                </div>
                <div className="flex-1">
                  <p className="text-sm font-medium text-gray-900">New reference submitted</p>
                  <p className="text-xs text-gray-500">2 minutes ago</p>
                </div>
              </div>
              <div className="flex items-center space-x-3 pb-3 border-b border-gray-100">
                <div className="h-8 w-8 bg-blue-100 rounded-full flex items-center justify-center">
                  <FileText className="h-4 w-4 text-blue-600" />
                </div>
                <div className="flex-1">
                  <p className="text-sm font-medium text-gray-900">Application processed</p>
                  <p className="text-xs text-gray-500">15 minutes ago</p>
                </div>
              </div>
              <div className="flex items-center space-x-3">
                <div className="h-8 w-8 bg-purple-100 rounded-full flex items-center justify-center">
                  <TrendingUp className="h-4 w-4 text-purple-600" />
                </div>
                <div className="flex-1">
                  <p className="text-sm font-medium text-gray-900">Response rate improved</p>
                  <p className="text-xs text-gray-500">1 hour ago</p>
                </div>
              </div>
            </div>
          </div>
        </div>
       

      </div>
    </div>
  );
}