import { useState, useEffect } from 'react';
import { BarChart3, TrendingUp, Users, FileText, Activity } from 'lucide-react';
import { supabase } from '../../lib/supabase';

// Recharts Imports
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  BarChart, Bar, PieChart, Pie, Cell, AreaChart, Area
} from 'recharts';

const PIE_COLORS = ['#3b82f6', '#10b981', '#f87171', '#f59e0b', '#8b5cf6']; // blue, green, red, orange, purple

// --- CHART COMPONENTS ---

const HorizontalBarChart = ({ data }: { data: any[] }) => (
  <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 h-full">
    <h2 className="text-lg font-bold text-gray-900 mb-4">Applications by Role</h2>
    <ResponsiveContainer width="100%" height={250}>
      <BarChart data={data} layout="vertical" margin={{ top: 5, right: 20, left: 20, bottom: 5 }}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis type="number" stroke="#6b7280" />
        <YAxis dataKey="role" type="category" stroke="#6b7280" width={120} />
        <Tooltip />
        <Bar dataKey="count" fill="#10b981" name="Applications" />
      </BarChart>
    </ResponsiveContainer>
  </div>
);

const StatusPieChart = ({ data }: { data: any[] }) => (
  <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 h-full">
    <h2 className="text-lg font-bold text-gray-900 mb-4">Application Status Distribution</h2>
    <ResponsiveContainer width="100%" height={250}>
      <PieChart>
        <Pie
          data={data}
          dataKey="value"
          nameKey="name"
          cx="50%"
          cy="50%"
          outerRadius={100}
          labelLine={false}
          label={({ name, percent }) => `${name} (${((percent ?? 0) * 100).toFixed(0)}%)`}
        >
          {data.map((_entry, index) => (
            <Cell key={`cell-${index}`} fill={PIE_COLORS[index % PIE_COLORS.length]} />
          ))}
        </Pie>
        <Tooltip />
      </PieChart>
    </ResponsiveContainer>
  </div>
);

const SystemActivityAreaChart = ({ data }: { data: any[] }) => (
  <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 h-full">
    <h2 className="text-lg font-bold text-gray-900 mb-4">Applications Over Time (Last 30 Days)</h2>
    <ResponsiveContainer width="100%" height={250}>
      <AreaChart data={data} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="date" stroke="#6b7280" />
        <YAxis stroke="#6b7280" />
        <Tooltip />
        <Area type="monotone" dataKey="count" stroke="#f97316" fill="#fed7aa" name="Applications" />
      </AreaChart>
    </ResponsiveContainer>
  </div>
);

const TrendLineChart = ({ data }: { data: any[] }) => (
  <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 h-full">
    <h2 className="text-lg font-bold text-gray-900 mb-4">Applications & References Trend</h2>
    <ResponsiveContainer width="100%" height={250}>
      <LineChart data={data} margin={{ top: 5, right: 20, left: 10, bottom: 5 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" />
        <XAxis dataKey="date" stroke="#6b7280" />
        <YAxis stroke="#6b7280" />
        <Tooltip />
        <Line type="monotone" dataKey="applications" stroke="#3b82f6" strokeWidth={2} dot={{ r: 4 }} activeDot={{ r: 8 }} name="Applications" />
        <Line type="monotone" dataKey="references" stroke="#10b981" strokeWidth={2} dot={{ r: 4 }} activeDot={{ r: 8 }} name="References" />
      </LineChart>
    </ResponsiveContainer>
  </div>
);

// --- MAIN COMPONENT ---

export function AnalyticsDashboard() {
  const [loading, setLoading] = useState(true);
  const [metrics, setMetrics] = useState({
    totalApplications: 0,
    activeReferences: 0,
    responseRate: 0,
    avgProcessingTime: 0,
    prevTotalApplications: 0,
    prevActiveReferences: 0,
    prevResponseRate: 0,
    prevAvgProcessingTime: 0
  });
  
  const [statusData, setStatusData] = useState<any[]>([]);
  const [roleData, setRoleData] = useState<any[]>([]);
  const [timeSeriesData, setTimeSeriesData] = useState<any[]>([]);
  const [trendData, setTrendData] = useState<any[]>([]);

  useEffect(() => {
    fetchAnalyticsData();
  }, []);

  const fetchAnalyticsData = async () => {
    try {
      setLoading(true);

      // Fetch all applications
      const { data: applications, error: appsError } = await supabase
        .from('applications')
        .select('*')
        .order('created_at', { ascending: false });

      if (appsError) throw appsError;

      // Fetch all references
      const { data: references, error: refsError } = await supabase
        .from('references')
        .select('*');

      if (refsError) throw refsError;

      // Calculate metrics
      const now = new Date();
      const thirtyDaysAgo = new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000);
      const sixtyDaysAgo = new Date(now.getTime() - 60 * 24 * 60 * 60 * 1000);

      // Current period (last 30 days)
      const recentApps = applications?.filter(app => new Date(app.created_at) >= thirtyDaysAgo) || [];
      const recentRefs = references?.filter(ref => new Date(ref.created_at) >= thirtyDaysAgo) || [];
      
      // Previous period (30-60 days ago)
      const prevApps = applications?.filter(app => {
        const date = new Date(app.created_at);
        return date >= sixtyDaysAgo && date < thirtyDaysAgo;
      }) || [];
      const prevRefs = references?.filter(ref => {
        const date = new Date(ref.created_at);
        return date >= sixtyDaysAgo && date < thirtyDaysAgo;
      }) || [];

      // Response rate calculation
      const respondedRefs = references?.filter(ref => ref.status === 'responded').length || 0;
      const totalRefs = references?.length || 1;
      const currentResponseRate = (respondedRefs / totalRefs) * 100;

      const prevRespondedRefs = prevRefs.filter(ref => ref.status === 'responded').length || 0;
      const prevTotalRefs = prevRefs.length || 1;
      const prevResponseRate = (prevRespondedRefs / prevTotalRefs) * 100;

      // Calculate average processing time
      const completedApps = applications?.filter(app => app.status === 'completed') || [];
      let totalProcessingTime = 0;
      completedApps.forEach(app => {
        const created = new Date(app.created_at).getTime();
        const updated = new Date(app.updated_at).getTime();
        const diffDays = (updated - created) / (1000 * 60 * 60 * 24);
        totalProcessingTime += diffDays;
      });
      const avgProcessingTime = completedApps.length > 0 ? totalProcessingTime / completedApps.length : 0;

      // Previous period processing time
      const prevCompletedApps = prevApps.filter(app => app.status === 'completed');
      let prevTotalProcessingTime = 0;
      prevCompletedApps.forEach(app => {
        const created = new Date(app.created_at).getTime();
        const updated = new Date(app.updated_at).getTime();
        const diffDays = (updated - created) / (1000 * 60 * 60 * 24);
        prevTotalProcessingTime += diffDays;
      });
      const prevAvgProcessingTime = prevCompletedApps.length > 0 ? prevTotalProcessingTime / prevCompletedApps.length : avgProcessingTime;

      setMetrics({
        totalApplications: applications?.length || 0,
        activeReferences: references?.length || 0,
        responseRate: currentResponseRate,
        avgProcessingTime: avgProcessingTime,
        prevTotalApplications: prevApps.length,
        prevActiveReferences: prevRefs.length,
        prevResponseRate: prevResponseRate,
        prevAvgProcessingTime: prevAvgProcessingTime
      });

      // Status distribution
      const statusCounts = applications?.reduce((acc: any, app) => {
        const status = app.status.charAt(0).toUpperCase() + app.status.slice(1);
        acc[status] = (acc[status] || 0) + 1;
        return acc;
      }, {});

      const statusChartData = Object.entries(statusCounts || {}).map(([name, value]) => ({
        name,
        value
      }));
      setStatusData(statusChartData);

      // Applications by role (top 5)
      const roleCounts = applications?.reduce((acc: any, app) => {
        acc[app.role] = (acc[app.role] || 0) + 1;
        return acc;
      }, {});

      const roleChartData = Object.entries(roleCounts || {})
        .map(([role, count]) => ({ role, count }))
        .sort((a: any, b: any) => b.count - a.count)
        .slice(0, 5);
      setRoleData(roleChartData);

      // Time series data (last 30 days)
      const timeSeriesMap: any = {};
      for (let i = 29; i >= 0; i--) {
        const date = new Date(now);
        date.setDate(date.getDate() - i);
        const dateStr = date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
        timeSeriesMap[dateStr] = { date: dateStr, count: 0 };
      }

      recentApps.forEach(app => {
        const dateStr = new Date(app.created_at).toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
        if (timeSeriesMap[dateStr]) {
          timeSeriesMap[dateStr].count++;
        }
      });

      setTimeSeriesData(Object.values(timeSeriesMap));

      // Trend data (last 7 weeks - weekly aggregation)
      const weeklyData: any = {};
      for (let i = 6; i >= 0; i--) {
        const weekStart = new Date(now);
        weekStart.setDate(weekStart.getDate() - (i * 7));
        const weekLabel = `Wk ${7 - i}`;
        weeklyData[weekLabel] = { date: weekLabel, applications: 0, references: 0 };
      }

      applications?.forEach(app => {
        const appDate = new Date(app.created_at);
        const weeksDiff = Math.floor((now.getTime() - appDate.getTime()) / (7 * 24 * 60 * 60 * 1000));
        if (weeksDiff < 7) {
          const weekLabel = `Wk ${7 - weeksDiff}`;
          if (weeklyData[weekLabel]) {
            weeklyData[weekLabel].applications++;
          }
        }
      });

      references?.forEach(ref => {
        const refDate = new Date(ref.created_at);
        const weeksDiff = Math.floor((now.getTime() - refDate.getTime()) / (7 * 24 * 60 * 60 * 1000));
        if (weeksDiff < 7) {
          const weekLabel = `Wk ${7 - weeksDiff}`;
          if (weeklyData[weekLabel]) {
            weeklyData[weekLabel].references++;
          }
        }
      });

      setTrendData(Object.values(weeklyData));

    } catch (error) {
      console.error('Error fetching analytics:', error);
    } finally {
      setLoading(false);
    }
  };

  const calculateChange = (current: number, previous: number) => {
    if (previous === 0) return current > 0 ? '+100%' : '0%';
    const change = ((current - previous) / previous) * 100;
    return `${change >= 0 ? '+' : ''}${change.toFixed(1)}%`;
  };

  const getMetricCards = () => [
    {
      title: 'Total Applications',
      value: metrics.totalApplications.toString(),
      change: calculateChange(metrics.totalApplications, metrics.prevTotalApplications),
      trend: metrics.totalApplications >= metrics.prevTotalApplications ? 'up' : 'down',
      icon: FileText,
      color: 'blue'
    },
    {
      title: 'Active References',
      value: metrics.activeReferences.toString(),
      change: calculateChange(metrics.activeReferences, metrics.prevActiveReferences),
      trend: metrics.activeReferences >= metrics.prevActiveReferences ? 'up' : 'down',
      icon: Users,
      color: 'green'
    },
    {
      title: 'Response Rate',
      value: `${metrics.responseRate.toFixed(1)}%`,
      change: calculateChange(metrics.responseRate, metrics.prevResponseRate),
      trend: metrics.responseRate >= metrics.prevResponseRate ? 'up' : 'down',
      icon: TrendingUp,
      color: 'purple'
    },
    {
      title: 'Avg. Processing Time',
      value: `${metrics.avgProcessingTime.toFixed(1)} days`,
      change: calculateChange(metrics.prevAvgProcessingTime, metrics.avgProcessingTime), // Reversed: lower is better
      trend: metrics.avgProcessingTime <= metrics.prevAvgProcessingTime ? 'up' : 'down',
      icon: Activity,
      color: 'indigo'
    }
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
          <p className="text-gray-600">Loading analytics...</p>
        </div>
      </div>
    );
  }

  const metricCards = getMetricCards();

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Key Metrics */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {metricCards.map((metric, index) => {
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

        {/* Charts Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          <TrendLineChart data={trendData} />
          <HorizontalBarChart data={roleData} />
          <StatusPieChart data={statusData} />
          <SystemActivityAreaChart data={timeSeriesData} />
        </div>

        {/* Additional Info Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-8">
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <h3 className="text-lg font-bold text-gray-900 mb-4">Quick Actions</h3>
            <div className="space-y-3">
              <button 
                onClick={() => fetchAnalyticsData()}
                className="w-full text-left px-4 py-3 bg-gray-50 hover:bg-gray-100 rounded-lg transition-colors flex items-center justify-between"
              >
                <span className="text-gray-700">Refresh Dashboard</span>
                <span className="text-blue-600">↻</span>
              </button>
              <button className="w-full text-left px-4 py-3 bg-gray-50 hover:bg-gray-100 rounded-lg transition-colors flex items-center justify-between">
                <span className="text-gray-700">Export Dashboard Data</span>
                <span className="text-blue-600">→</span>
              </button>
              <button className="w-full text-left px-4 py-3 bg-gray-50 hover:bg-gray-100 rounded-lg transition-colors flex items-center justify-between">
                <span className="text-gray-700">Schedule Reports</span>
                <span className="text-blue-600">→</span>
              </button>
            </div>
          </div>

          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <h3 className="text-lg font-bold text-gray-900 mb-4">Summary</h3>
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <span className="text-gray-600">Total Applications</span>
                <span className="font-bold text-gray-900">{metrics.totalApplications}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-600">Total References</span>
                <span className="font-bold text-gray-900">{metrics.activeReferences}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-600">Response Rate</span>
                <span className="font-bold text-gray-900">{metrics.responseRate.toFixed(1)}%</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-600">Avg. Processing</span>
                <span className="font-bold text-gray-900">{metrics.avgProcessingTime.toFixed(1)} days</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}