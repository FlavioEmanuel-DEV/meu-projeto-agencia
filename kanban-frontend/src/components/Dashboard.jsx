import React, { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { 
  DropdownMenu, 
  DropdownMenuContent, 
  DropdownMenuItem, 
  DropdownMenuTrigger 
} from '@/components/ui/dropdown-menu';
import { 
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { 
  Plus, 
  LogOut, 
  User, 
  Calendar, 
  Clock,
  MoreVertical,
  Filter,
  Edit,
  Trash2,
  GripVertical
} from 'lucide-react';
import {
  DndContext,
  DragOverlay,
  closestCorners,
  KeyboardSensor,
  PointerSensor,
  useSensor,
  useSensors,
} from '@dnd-kit/core';
import {
  arrayMove,
  SortableContext,
  sortableKeyboardCoordinates,
  verticalListSortingStrategy,
} from '@dnd-kit/sortable';
import {
  useSortable,
} from '@dnd-kit/sortable';
import { CSS } from '@dnd-kit/utilities';
import { useAuth } from '../contexts/AuthContext';
import ApiService from '../services/api';
import NotificationCenter from './NotificationCenter';

// Componente de cartão arrastável
const DraggableCard = ({ cartao, onEdit, onDelete }) => {
  const {
    attributes,
    listeners,
    setNodeRef,
    transform,
    transition,
    isDragging,
  } = useSortable({ id: cartao.id });

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
    opacity: isDragging ? 0.5 : 1,
  };

  const getStatusColor = (status) => {
    const colors = {
      'pendente': 'bg-gray-100 text-gray-800',
      'em_andamento': 'bg-blue-100 text-blue-800',
      'aprovado': 'bg-yellow-100 text-yellow-800',
      'concluido': 'bg-green-100 text-green-800'
    };
    return colors[status] || 'bg-gray-100 text-gray-800';
  };

  const getStatusText = (status) => {
    const texts = {
      'pendente': 'Pendente',
      'em_andamento': 'Em Andamento',
      'aprovado': 'Aprovação',
      'concluido': 'Concluído'
    };
    return texts[status] || status;
  };

  const formatDate = (dateString) => {
    if (!dateString) return '';
    const date = new Date(dateString);
    return date.toLocaleDateString('pt-BR');
  };

  const isOverdue = (dateString) => {
    if (!dateString) return false;
    const date = new Date(dateString);
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    return date < today;
  };

  return (
    <Card 
      ref={setNodeRef} 
      style={style} 
      className="cursor-pointer hover:shadow-md transition-shadow"
      {...attributes}
    >
      <CardHeader className="pb-2">
        <div className="flex items-start justify-between">
          <div className="flex items-start space-x-2 flex-1">
            <div 
              {...listeners}
              className="cursor-grab active:cursor-grabbing p-1 hover:bg-gray-100 rounded"
            >
              <GripVertical className="h-4 w-4 text-gray-400" />
            </div>
            <CardTitle className="text-sm font-medium flex-1">
              {cartao.titulo}
            </CardTitle>
          </div>
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" size="sm" className="h-6 w-6 p-0">
                <MoreVertical className="h-3 w-3" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              <DropdownMenuItem onClick={() => onEdit(cartao)}>
                <Edit className="h-4 w-4 mr-2" />
                Editar
              </DropdownMenuItem>
              <DropdownMenuItem 
                className="text-red-600"
                onClick={() => onDelete(cartao.id)}
              >
                <Trash2 className="h-4 w-4 mr-2" />
                Excluir
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </CardHeader>
      <CardContent className="pt-0">
        {cartao.descricao && (
          <p className="text-xs text-gray-600 mb-2 line-clamp-2">
            {cartao.descricao}
          </p>
        )}
        
        <div className="flex items-center justify-between text-xs">
          <Badge 
            className={getStatusColor(cartao.status)}
            variant="secondary"
          >
            {getStatusText(cartao.status)}
          </Badge>
          
          {cartao.prazo_entrega && (
            <div className={`flex items-center space-x-1 ${
              isOverdue(cartao.prazo_entrega) 
                ? 'text-red-600' 
                : 'text-gray-500'
            }`}>
              <Calendar className="h-3 w-3" />
              <span>{formatDate(cartao.prazo_entrega)}</span>
            </div>
          )}
        </div>
        
        {cartao.responsavel_nome && (
          <div className="flex items-center space-x-2 mt-2">
            <Avatar className="h-6 w-6">
              <AvatarFallback className="text-xs">
                {cartao.responsavel_nome.charAt(0).toUpperCase()}
              </AvatarFallback>
            </Avatar>
            <span className="text-xs text-gray-600">
              {cartao.responsavel_nome}
            </span>
          </div>
        )}
      </CardContent>
    </Card>
  );
};

// Componente de coluna com drop zone
const DroppableColumn = ({ coluna, cartoes, onAddCard, onEditCard, onDeleteCard }) => {
  return (
    <div className="bg-gray-100 rounded-lg p-4">
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-semibold text-gray-900">
          {coluna.titulo}
        </h3>
        <Badge variant="secondary">
          {cartoes.length}
        </Badge>
      </div>

      <SortableContext items={cartoes.map(c => c.id)} strategy={verticalListSortingStrategy}>
        <div className="space-y-3 min-h-[200px]">
          {cartoes.map((cartao) => (
            <DraggableCard
              key={cartao.id}
              cartao={cartao}
              onEdit={onEditCard}
              onDelete={onDeleteCard}
            />
          ))}
          
          <Button 
            variant="ghost" 
            className="w-full border-2 border-dashed border-gray-300 h-12"
            onClick={() => onAddCard(coluna.id)}
          >
            <Plus className="h-4 w-4 mr-2" />
            Adicionar Cartão
          </Button>
        </div>
      </SortableContext>
    </div>
  );
};

const Dashboard = () => {
  const { user, logout, isGestor } = useAuth();
  const [quadros, setQuadros] = useState([]);
  const [quadroSelecionado, setQuadroSelecionado] = useState(null);
  const [loading, setLoading] = useState(true);
  const [filtroSetor, setFiltroSetor] = useState('');
  const [usuarios, setUsuarios] = useState([]);
  const [clientes, setClientes] = useState([]);
  const [activeId, setActiveId] = useState(null);
  
  // Estados para modais
  const [modalCartaoAberto, setModalCartaoAberto] = useState(false);
  const [cartaoEditando, setCartaoEditando] = useState(null);
  const [novoCartao, setNovoCartao] = useState({
    titulo: '',
    descricao: '',
    responsavel_id: '',
    cliente_id: '',
    prazo_entrega: '',
    coluna_id: ''
  });

  const sensors = useSensors(
    useSensor(PointerSensor),
    useSensor(KeyboardSensor, {
      coordinateGetter: sortableKeyboardCoordinates,
    })
  );

  useEffect(() => {
    carregarDados();
  }, []);

  const carregarDados = async () => {
    try {
      setLoading(true);
      const [quadrosData, usuariosData, clientesData] = await Promise.all([
        ApiService.getQuadros(),
        isGestor ? ApiService.getUsers() : Promise.resolve([]),
        ApiService.getClientes()
      ]);
      
      setQuadros(quadrosData);
      setUsuarios(usuariosData);
      setClientes(clientesData);
      
      // Selecionar primeiro quadro automaticamente
      if (quadrosData.length > 0) {
        setQuadroSelecionado(quadrosData[0]);
      }
    } catch (error) {
      console.error('Erro ao carregar dados:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleDragStart = (event) => {
    setActiveId(event.active.id);
  };

  const handleDragEnd = async (event) => {
    const { active, over } = event;
    setActiveId(null);

    if (!over) return;

    const activeId = active.id;
    const overId = over.id;

    if (activeId === overId) return;

    // Encontrar o cartão que está sendo movido
    const activeCartao = quadroSelecionado.colunas
      .flatMap(col => col.cartoes)
      .find(cartao => cartao.id === activeId);

    if (!activeCartao) return;

    // Determinar a coluna de destino
    let targetColunaId;
    let targetIndex;

    // Verificar se foi solto sobre outro cartão
    const overCartao = quadroSelecionado.colunas
      .flatMap(col => col.cartoes)
      .find(cartao => cartao.id === overId);

    if (overCartao) {
      // Solto sobre outro cartão - usar a coluna desse cartão
      const targetColuna = quadroSelecionado.colunas
        .find(col => col.cartoes.some(cartao => cartao.id === overId));
      targetColunaId = targetColuna.id;
      targetIndex = targetColuna.cartoes.findIndex(cartao => cartao.id === overId);
    } else {
      // Solto diretamente na coluna
      const targetColuna = quadroSelecionado.colunas.find(col => col.id === overId);
      if (targetColuna) {
        targetColunaId = targetColuna.id;
        targetIndex = targetColuna.cartoes.length;
      } else {
        return;
      }
    }

    try {
      // Atualizar no backend
      await ApiService.moveCartao(activeId, targetColunaId, targetIndex);
      
      // Recarregar quadro
      const quadroAtualizado = await ApiService.getQuadro(quadroSelecionado.id);
      setQuadroSelecionado(quadroAtualizado);
    } catch (error) {
      console.error('Erro ao mover cartão:', error);
      alert('Erro ao mover cartão: ' + error.message);
    }
  };

  const handleCriarCartao = async (colunaId) => {
    setNovoCartao({
      titulo: '',
      descricao: '',
      responsavel_id: user.id,
      cliente_id: '',
      prazo_entrega: '',
      coluna_id: colunaId
    });
    setCartaoEditando(null);
    setModalCartaoAberto(true);
  };

  const handleEditarCartao = (cartao) => {
    setNovoCartao({
      titulo: cartao.titulo,
      descricao: cartao.descricao,
      responsavel_id: cartao.responsavel_id,
      cliente_id: cartao.cliente_id,
      prazo_entrega: cartao.prazo_entrega ? cartao.prazo_entrega.split('T')[0] : '',
      coluna_id: cartao.coluna_id
    });
    setCartaoEditando(cartao);
    setModalCartaoAberto(true);
  };

  const handleSalvarCartao = async () => {
    try {
      if (cartaoEditando) {
        await ApiService.updateCartao(cartaoEditando.id, novoCartao);
      } else {
        await ApiService.createCartao(novoCartao);
      }
      
      // Recarregar quadro atual
      const quadroAtualizado = await ApiService.getQuadro(quadroSelecionado.id);
      setQuadroSelecionado(quadroAtualizado);
      
      setModalCartaoAberto(false);
      setNovoCartao({
        titulo: '',
        descricao: '',
        responsavel_id: '',
        cliente_id: '',
        prazo_entrega: '',
        coluna_id: ''
      });
    } catch (error) {
      console.error('Erro ao salvar cartão:', error);
      alert('Erro ao salvar cartão: ' + error.message);
    }
  };

  const handleDeletarCartao = async (cartaoId) => {
    if (confirm('Tem certeza que deseja deletar este cartão?')) {
      try {
        await ApiService.deleteCartao(cartaoId);
        
        // Recarregar quadro atual
        const quadroAtualizado = await ApiService.getQuadro(quadroSelecionado.id);
        setQuadroSelecionado(quadroAtualizado);
      } catch (error) {
        console.error('Erro ao deletar cartão:', error);
        alert('Erro ao deletar cartão: ' + error.message);
      }
    }
  };

  const setores = ['Social Media', 'Design', 'Tráfego Pago', 'Audiovisual', 'Comercial', 'Gestão'];

  const quadrosFiltrados = filtroSetor 
    ? quadros.filter(q => q.setor === filtroSetor)
    : quadros;

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
          <p className="mt-4 text-gray-600">Carregando...</p>
        </div>
      </div>
    );
  }

  return (
    <DndContext
      sensors={sensors}
      collisionDetection={closestCorners}
      onDragStart={handleDragStart}
      onDragEnd={handleDragEnd}
    >
      <div className="min-h-screen bg-gray-50">
        {/* Header */}
        <header className="bg-white shadow-sm border-b">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between items-center py-4">
              <div className="flex items-center space-x-4">
                <h1 className="text-2xl font-bold text-gray-900">
                  Sistema Kanban
                </h1>
                <Badge variant="outline" className="text-sm">
                  {user?.setor}
                </Badge>
              </div>
              
              <div className="flex items-center space-x-4">
                <DropdownMenu>
                  <DropdownMenuTrigger asChild>
                    <Button variant="ghost" size="sm">
                      <Filter className="h-4 w-4 mr-2" />
                      Filtrar
                    </Button>
                  </DropdownMenuTrigger>
                  <DropdownMenuContent align="end">
                    <DropdownMenuItem onClick={() => setFiltroSetor('')}>
                      Todos os Setores
                    </DropdownMenuItem>
                    {setores.map(setor => (
                      <DropdownMenuItem 
                        key={setor}
                        onClick={() => setFiltroSetor(setor)}
                      >
                        {setor}
                      </DropdownMenuItem>
                    ))}
                  </DropdownMenuContent>
                </DropdownMenu>

                <NotificationCenter user={user} />

                <DropdownMenu>
                  <DropdownMenuTrigger asChild>
                    <Button variant="ghost" className="flex items-center space-x-2">
                      <Avatar className="h-8 w-8">
                        <AvatarFallback>
                          {user?.nome?.charAt(0)?.toUpperCase()}
                        </AvatarFallback>
                      </Avatar>
                      <span className="hidden md:block">{user?.nome}</span>
                    </Button>
                  </DropdownMenuTrigger>
                  <DropdownMenuContent align="end">
                    <DropdownMenuItem>
                      <User className="h-4 w-4 mr-2" />
                      Perfil
                    </DropdownMenuItem>
                    <DropdownMenuItem onClick={logout}>
                      <LogOut className="h-4 w-4 mr-2" />
                      Sair
                    </DropdownMenuItem>
                  </DropdownMenuContent>
                </DropdownMenu>
              </div>
            </div>
          </div>
        </header>

        {/* Sidebar com lista de quadros */}
        <div className="flex">
          <aside className="w-64 bg-white shadow-sm h-screen sticky top-0">
            <div className="p-4">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-lg font-semibold text-gray-900">Quadros</h2>
                {isGestor && (
                  <Button size="sm" variant="outline">
                    <Plus className="h-4 w-4" />
                  </Button>
                )}
              </div>
              
              <div className="space-y-2">
                {quadrosFiltrados.map((quadro) => (
                  <button
                    key={quadro.id}
                    onClick={() => setQuadroSelecionado(quadro)}
                    className={`w-full text-left p-3 rounded-lg transition-colors ${
                      quadroSelecionado?.id === quadro.id
                        ? 'bg-blue-50 border-blue-200 border'
                        : 'hover:bg-gray-50'
                    }`}
                  >
                    <div className="font-medium text-sm">{quadro.titulo}</div>
                    <div className="text-xs text-gray-500 mt-1">
                      {quadro.tipo === 'Setor' ? quadro.setor : quadro.cliente_nome}
                    </div>
                  </button>
                ))}
              </div>
            </div>
          </aside>

          {/* Área principal do Kanban */}
          <main className="flex-1 p-6">
            {quadroSelecionado ? (
              <div>
                <div className="mb-6">
                  <h2 className="text-2xl font-bold text-gray-900">
                    {quadroSelecionado.titulo}
                  </h2>
                  <p className="text-gray-600">
                    {quadroSelecionado.tipo === 'Setor' 
                      ? `Setor: ${quadroSelecionado.setor}`
                      : `Cliente: ${quadroSelecionado.cliente_nome}`
                    }
                  </p>
                </div>

                {/* Colunas do Kanban */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                  {quadroSelecionado.colunas?.map((coluna) => (
                    <DroppableColumn
                      key={coluna.id}
                      coluna={coluna}
                      cartoes={coluna.cartoes || []}
                      onAddCard={handleCriarCartao}
                      onEditCard={handleEditarCartao}
                      onDeleteCard={handleDeletarCartao}
                    />
                  ))}
                </div>
              </div>
            ) : (
              <div className="text-center py-12">
                <h3 className="text-lg font-medium text-gray-900 mb-2">
                  Nenhum quadro selecionado
                </h3>
                <p className="text-gray-600">
                  Selecione um quadro na barra lateral para visualizar as tarefas
                </p>
              </div>
            )}
          </main>
        </div>

        {/* Modal de Criação/Edição de Cartão */}
        <Dialog open={modalCartaoAberto} onOpenChange={setModalCartaoAberto}>
          <DialogContent className="sm:max-w-[425px]">
            <DialogHeader>
              <DialogTitle>
                {cartaoEditando ? 'Editar Cartão' : 'Novo Cartão'}
              </DialogTitle>
              <DialogDescription>
                {cartaoEditando ? 'Edite as informações do cartão.' : 'Preencha as informações para criar um novo cartão.'}
              </DialogDescription>
            </DialogHeader>
            <div className="grid gap-4 py-4">
              <div className="grid gap-2">
                <Label htmlFor="titulo">Título</Label>
                <Input
                  id="titulo"
                  value={novoCartao.titulo}
                  onChange={(e) => setNovoCartao({...novoCartao, titulo: e.target.value})}
                  placeholder="Digite o título do cartão"
                />
              </div>
              
              <div className="grid gap-2">
                <Label htmlFor="descricao">Descrição</Label>
                <Textarea
                  id="descricao"
                  value={novoCartao.descricao}
                  onChange={(e) => setNovoCartao({...novoCartao, descricao: e.target.value})}
                  placeholder="Digite a descrição do cartão"
                  rows={3}
                />
              </div>
              
              <div className="grid gap-2">
                <Label htmlFor="responsavel">Responsável</Label>
                <Select 
                  value={novoCartao.responsavel_id.toString()} 
                  onValueChange={(value) => setNovoCartao({...novoCartao, responsavel_id: parseInt(value)})}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Selecione o responsável" />
                  </SelectTrigger>
                  <SelectContent>
                    {usuarios.length > 0 ? usuarios.map((usuario) => (
                      <SelectItem key={usuario.id} value={usuario.id.toString()}>
                        {usuario.nome} ({usuario.setor})
                      </SelectItem>
                    )) : (
                      <SelectItem value={user.id.toString()}>
                        {user.nome} ({user.setor})
                      </SelectItem>
                    )}
                  </SelectContent>
                </Select>
              </div>
              
              <div className="grid gap-2">
                <Label htmlFor="cliente">Cliente</Label>
                <Select 
                  value={novoCartao.cliente_id.toString()} 
                  onValueChange={(value) => setNovoCartao({...novoCartao, cliente_id: parseInt(value)})}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Selecione o cliente" />
                  </SelectTrigger>
                  <SelectContent>
                    {clientes.map((cliente) => (
                      <SelectItem key={cliente.id} value={cliente.id.toString()}>
                        {cliente.nome}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              
              <div className="grid gap-2">
                <Label htmlFor="prazo">Prazo de Entrega</Label>
                <Input
                  id="prazo"
                  type="date"
                  value={novoCartao.prazo_entrega}
                  onChange={(e) => setNovoCartao({...novoCartao, prazo_entrega: e.target.value})}
                />
              </div>
            </div>
            
            <div className="flex justify-end space-x-2">
              <Button variant="outline" onClick={() => setModalCartaoAberto(false)}>
                Cancelar
              </Button>
              <Button onClick={handleSalvarCartao}>
                {cartaoEditando ? 'Salvar' : 'Criar'}
              </Button>
            </div>
          </DialogContent>
        </Dialog>

        <DragOverlay>
          {activeId ? (
            <Card className="cursor-grabbing opacity-80">
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium">
                  Movendo cartão...
                </CardTitle>
              </CardHeader>
            </Card>
          ) : null}
        </DragOverlay>
      </div>
    </DndContext>
  );
};

export default Dashboard;

