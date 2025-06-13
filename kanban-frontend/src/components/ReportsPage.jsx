import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  Legend, 
  PieChart, 
  Pie, 
  Cell,
  LineChart,
  Line,
  ResponsiveContainer
} from 'recharts';
import { 
  TrendingUp, 
  TrendingDown, 
  Clock, 
  CheckCircle, 
  AlertTriangle,
  Users,
  BarChart3,
  Download,
  Calendar,
  Target
} from 'lucide-react';
import ApiService from '../services/api';

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8'];

const ReportsPage = () => {
  const [loading, setLoading] = useState(false);
  const [dashboardData, setDashboardData] = useState(null);
  const [produtividadeData, setProdutividadeData] = useState(null);
  const [prazosData, setPrazosData] = useState(null);
  const [filtros, setFiltros] = useState({
    dataInicio: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
    dataFim: new Date().toISOString().split('T')[0],
    periodo: '30'
  });

  useEffect(() => {
    carregarDados();
  }, [filtros]);

  const carregarDados = async () => {
    try {
      setLoading(true);
      
      const [dashboard, produtividade, prazos] = await Promise.all([
        ApiService.getDashboardRelatorio(filtros.dataInicio, filtros.dataFim),
        ApiService.getProdutividadeRelatorio(filtros.periodo),
        ApiService.getPrazosRelatorio()
      ]);
      
      setDashboardData(dashboard);
      setProdutividadeData(produtividade);
      setPrazosData(prazos);
    } catch (error) {
      console.error('Erro ao carregar relatórios:', error);
    } finally {
      setLoading(false);
    }
  };

  const exportarRelatorio = async (tipo) => {
    try {
      const response = await ApiService.exportarRelatorio(tipo, 'json');
      
      // Criar download do arquivo
      const blob = new Blob([JSON.stringify(response, null, 2)], { type: 'application/json' });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `relatorio_${tipo}_${new Date().toISOString().split('T')[0]}.json`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (error) {
      console.error('Erro ao exportar relatório:', error);
    }
  };

  const StatCard = ({ title, value, subtitle, icon: Icon, trend, color = "blue" }) => (
    <Card>
      <CardContent className="p-6">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm font-medium text-gray-600">{title}</p>
            <p className={`text-2xl font-bold text-${color}-600`}>{value}</p>
            {subtitle && (
              <p className="text-xs text-gray-500 mt-1">{subtitle}</p>
            )}
          </div>
          <div className={`p-3 bg-${color}-100 rounded-full`}>
            <Icon className={`h-6 w-6 text-${color}-600`} />
          </div>
        </div>
        {trend && (
          <div className="flex items-center mt-4">
            {trend > 0 ? (
              <TrendingUp className="h-4 w-4 text-green-500 mr-1" />
            ) : (
              <TrendingDown className="h-4 w-4 text-red-500 mr-1" />
            )}
            <span className={`text-sm ${trend > 0 ? 'text-green-600' : 'text-red-600'}`}>
              {Math.abs(trend)}% vs período anterior
            </span>
          </div>
        )}
      </CardContent>
    </Card>
  );

  if (loading && !dashboardData) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
          <p className="mt-4 text-gray-600">Carregando relatórios...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Relatórios</h1>
              <p className="text-gray-600 mt-1">Análise de desempenho e produtividade</p>
            </div>
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                <Label htmlFor="dataInicio">De:</Label>
                <Input
                  id="dataInicio"
                  type="date"
                  value={filtros.dataInicio}
                  onChange={(e) => setFiltros({...filtros, dataInicio: e.target.value})}
                  className="w-40"
                />
              </div>
              <div className="flex items-center space-x-2">
                <Label htmlFor="dataFim">Até:</Label>
                <Input
                  id="dataFim"
                  type="date"
                  value={filtros.dataFim}
                  onChange={(e) => setFiltros({...filtros, dataFim: e.target.value})}
                  className="w-40"
                />
              </div>
              <Button onClick={carregarDados} disabled={loading}>
                Atualizar
              </Button>
            </div>
          </div>
        </div>

        <Tabs defaultValue="dashboard" className="space-y-6">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="dashboard">Dashboard</TabsTrigger>
            <TabsTrigger value="produtividade">Produtividade</TabsTrigger>
            <TabsTrigger value="prazos">Prazos</TabsTrigger>
          </TabsList>

          {/* Dashboard Tab */}
          <TabsContent value="dashboard" className="space-y-6">
            {dashboardData && (
              <>
                {/* Cards de Estatísticas */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                  <StatCard
                    title="Total de Cartões"
                    value={dashboardData.resumo.total_cartoes}
                    icon={BarChart3}
                    color="blue"
                  />
                  <StatCard
                    title="Taxa de Conclusão"
                    value={`${dashboardData.resumo.taxa_conclusao}%`}
                    icon={Target}
                    color="green"
                  />
                  <StatCard
                    title="Cartões Concluídos"
                    value={dashboardData.resumo.cartoes_concluidos}
                    icon={CheckCircle}
                    color="green"
                  />
                  <StatCard
                    title="Prazos Urgentes"
                    value={dashboardData.resumo.cartoes_prazo_urgente}
                    icon={AlertTriangle}
                    color="red"
                  />
                </div>

                {/* Gráficos */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  {/* Gráfico de Status */}
                  <Card>
                    <CardHeader>
                      <CardTitle>Distribuição por Status</CardTitle>
                      <Button 
                        size="sm" 
                        variant="outline"
                        onClick={() => exportarRelatorio('dashboard')}
                        className="ml-auto"
                      >
                        <Download className="h-4 w-4 mr-2" />
                        Exportar
                      </Button>
                    </CardHeader>
                    <CardContent>
                      <ResponsiveContainer width="100%" height={300}>
                        <PieChart>
                          <Pie
                            data={[
                              { name: 'Pendente', value: dashboardData.status_stats.pendente },
                              { name: 'Em Andamento', value: dashboardData.status_stats.em_andamento },
                              { name: 'Aprovação', value: dashboardData.status_stats.aprovado },
                              { name: 'Concluído', value: dashboardData.status_stats.concluido }
                            ]}
                            cx="50%"
                            cy="50%"
                            labelLine={false}
                            label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                            outerRadius={80}
                            fill="#8884d8"
                            dataKey="value"
                          >
                            {dashboardData.status_stats && Object.keys(dashboardData.status_stats).map((entry, index) => (
                              <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                            ))}
                          </Pie>
                          <Tooltip />
                        </PieChart>
                      </ResponsiveContainer>
                    </CardContent>
                  </Card>

                  {/* Gráfico por Setor */}
                  <Card>
                    <CardHeader>
                      <CardTitle>Cartões por Setor</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <ResponsiveContainer width="100%" height={300}>
                        <BarChart data={dashboardData.cartoes_por_setor}>
                          <CartesianGrid strokeDasharray="3 3" />
                          <XAxis dataKey="setor" />
                          <YAxis />
                          <Tooltip />
                          <Legend />
                          <Bar dataKey="total" fill="#8884d8" name="Total" />
                          <Bar dataKey="concluidos" fill="#82ca9d" name="Concluídos" />
                        </BarChart>
                      </ResponsiveContainer>
                    </CardContent>
                  </Card>
                </div>

                {/* Tabela de Clientes */}
                <Card>
                  <CardHeader>
                    <CardTitle>Desempenho por Cliente</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="overflow-x-auto">
                      <table className="w-full text-sm">
                        <thead>
                          <tr className="border-b">
                            <th className="text-left p-2">Cliente</th>
                            <th className="text-center p-2">Total</th>
                            <th className="text-center p-2">Concluídos</th>
                            <th className="text-center p-2">Taxa de Conclusão</th>
                          </tr>
                        </thead>
                        <tbody>
                          {dashboardData.cartoes_por_cliente.map((cliente, index) => (
                            <tr key={index} className="border-b hover:bg-gray-50">
                              <td className="p-2 font-medium">{cliente.cliente}</td>
                              <td className="text-center p-2">{cliente.total}</td>
                              <td className="text-center p-2">{cliente.concluidos}</td>
                              <td className="text-center p-2">
                                <Badge variant={cliente.taxa_conclusao >= 80 ? "default" : "secondary"}>
                                  {cliente.taxa_conclusao}%
                                </Badge>
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </CardContent>
                </Card>
              </>
            )}
          </TabsContent>

          {/* Produtividade Tab */}
          <TabsContent value="produtividade" className="space-y-6">
            {produtividadeData && (
              <>
                <div className="flex items-center justify-between">
                  <h2 className="text-xl font-semibold">Produtividade dos Usuários</h2>
                  <div className="flex items-center space-x-4">
                    <Select 
                      value={filtros.periodo} 
                      onValueChange={(value) => setFiltros({...filtros, periodo: value})}
                    >
                      <SelectTrigger className="w-40">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="7">Últimos 7 dias</SelectItem>
                        <SelectItem value="30">Últimos 30 dias</SelectItem>
                        <SelectItem value="90">Últimos 90 dias</SelectItem>
                      </SelectContent>
                    </Select>
                    <Button 
                      variant="outline"
                      onClick={() => exportarRelatorio('produtividade')}
                    >
                      <Download className="h-4 w-4 mr-2" />
                      Exportar
                    </Button>
                  </div>
                </div>

                <Card>
                  <CardContent className="p-6">
                    <div className="overflow-x-auto">
                      <table className="w-full text-sm">
                        <thead>
                          <tr className="border-b">
                            <th className="text-left p-3">Usuário</th>
                            <th className="text-left p-3">Setor</th>
                            <th className="text-center p-3">Total</th>
                            <th className="text-center p-3">Concluídos</th>
                            <th className="text-center p-3">Em Andamento</th>
                            <th className="text-center p-3">Taxa de Conclusão</th>
                            <th className="text-center p-3">Tempo Médio</th>
                          </tr>
                        </thead>
                        <tbody>
                          {produtividadeData.usuarios.map((usuario, index) => (
                            <tr key={index} className="border-b hover:bg-gray-50">
                              <td className="p-3 font-medium">{usuario.nome}</td>
                              <td className="p-3">
                                <Badge variant="outline">{usuario.setor}</Badge>
                              </td>
                              <td className="text-center p-3">{usuario.total_cartoes}</td>
                              <td className="text-center p-3">{usuario.concluidos}</td>
                              <td className="text-center p-3">{usuario.em_andamento}</td>
                              <td className="text-center p-3">
                                <Badge variant={usuario.taxa_conclusao >= 80 ? "default" : "secondary"}>
                                  {usuario.taxa_conclusao}%
                                </Badge>
                              </td>
                              <td className="text-center p-3">
                                {usuario.tempo_medio_conclusao} dias
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </CardContent>
                </Card>
              </>
            )}
          </TabsContent>

          {/* Prazos Tab */}
          <TabsContent value="prazos" className="space-y-6">
            {prazosData && (
              <>
                <div className="flex items-center justify-between">
                  <h2 className="text-xl font-semibold">Controle de Prazos</h2>
                  <Button 
                    variant="outline"
                    onClick={() => exportarRelatorio('prazos')}
                  >
                    <Download className="h-4 w-4 mr-2" />
                    Exportar
                  </Button>
                </div>

                {/* Cards de Resumo de Prazos */}
                <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                  <StatCard
                    title="Cartões Vencidos"
                    value={prazosData.resumo.total_vencidos}
                    icon={AlertTriangle}
                    color="red"
                  />
                  <StatCard
                    title="Vencendo Hoje"
                    value={prazosData.resumo.total_vencendo_hoje}
                    icon={Clock}
                    color="orange"
                  />
                  <StatCard
                    title="Vencendo em 3 dias"
                    value={prazosData.resumo.total_vencendo_3_dias}
                    icon={Calendar}
                    color="yellow"
                  />
                  <StatCard
                    title="Vencendo em 7 dias"
                    value={prazosData.resumo.total_vencendo_7_dias}
                    icon={Calendar}
                    color="blue"
                  />
                </div>

                {/* Listas de Cartões por Prazo */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  {/* Cartões Vencidos */}
                  <Card>
                    <CardHeader>
                      <CardTitle className="text-red-600">Cartões Vencidos</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-2 max-h-60 overflow-y-auto">
                        {prazosData.vencidos.length === 0 ? (
                          <p className="text-gray-500 text-center py-4">Nenhum cartão vencido</p>
                        ) : (
                          prazosData.vencidos.map((cartao) => (
                            <div key={cartao.id} className="p-3 border rounded-lg bg-red-50">
                              <h4 className="font-medium text-sm">{cartao.titulo}</h4>
                              <div className="flex justify-between items-center mt-1">
                                <span className="text-xs text-gray-600">{cartao.responsavel_nome}</span>
                                <Badge variant="destructive">
                                  {Math.abs(cartao.dias_restantes)} dias atraso
                                </Badge>
                              </div>
                            </div>
                          ))
                        )}
                      </div>
                    </CardContent>
                  </Card>

                  {/* Cartões Vencendo Hoje */}
                  <Card>
                    <CardHeader>
                      <CardTitle className="text-orange-600">Vencendo Hoje</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-2 max-h-60 overflow-y-auto">
                        {prazosData.vencendo_hoje.length === 0 ? (
                          <p className="text-gray-500 text-center py-4">Nenhum cartão vencendo hoje</p>
                        ) : (
                          prazosData.vencendo_hoje.map((cartao) => (
                            <div key={cartao.id} className="p-3 border rounded-lg bg-orange-50">
                              <h4 className="font-medium text-sm">{cartao.titulo}</h4>
                              <div className="flex justify-between items-center mt-1">
                                <span className="text-xs text-gray-600">{cartao.responsavel_nome}</span>
                                <Badge variant="secondary">Hoje</Badge>
                              </div>
                            </div>
                          ))
                        )}
                      </div>
                    </CardContent>
                  </Card>
                </div>
              </>
            )}
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
};

export default ReportsPage;

