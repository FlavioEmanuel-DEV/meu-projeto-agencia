import React, { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
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
} from '@/components/ui/dialog';
import { ScrollArea } from '@/components/ui/scroll-area';
import { 
  Bell, 
  BellRing, 
  Check, 
  CheckCheck, 
  Clock, 
  AlertTriangle,
  MessageSquare,
  UserPlus,
  ArrowRight
} from 'lucide-react';
import ApiService from '../services/api';

const NotificationCenter = ({ user }) => {
  const [notificacoes, setNotificacoes] = useState([]);
  const [naoLidas, setNaoLidas] = useState(0);
  const [loading, setLoading] = useState(false);
  const [modalAberto, setModalAberto] = useState(false);

  useEffect(() => {
    carregarNotificacoes();
    // Verificar notificações a cada 30 segundos
    const interval = setInterval(carregarNotificacoes, 30000);
    return () => clearInterval(interval);
  }, []);

  const carregarNotificacoes = async () => {
    try {
      const response = await ApiService.getNotificacoes();
      setNotificacoes(response.notificacoes || []);
      setNaoLidas(response.nao_lidas || 0);
    } catch (error) {
      console.error('Erro ao carregar notificações:', error);
    }
  };

  const marcarComoLida = async (notificacaoId) => {
    try {
      await ApiService.marcarNotificacaoLida(notificacaoId);
      await carregarNotificacoes();
    } catch (error) {
      console.error('Erro ao marcar notificação como lida:', error);
    }
  };

  const marcarTodasLidas = async () => {
    try {
      setLoading(true);
      await ApiService.marcarTodasNotificacoesLidas();
      await carregarNotificacoes();
    } catch (error) {
      console.error('Erro ao marcar todas como lidas:', error);
    } finally {
      setLoading(false);
    }
  };

  const getIconeNotificacao = (tipo) => {
    const icons = {
      'prazo_urgente': <AlertTriangle className="h-4 w-4 text-red-500" />,
      'prazo_proximo': <Clock className="h-4 w-4 text-yellow-500" />,
      'atribuicao': <UserPlus className="h-4 w-4 text-blue-500" />,
      'mudanca_status': <ArrowRight className="h-4 w-4 text-green-500" />,
      'comentario': <MessageSquare className="h-4 w-4 text-purple-500" />,
      'default': <Bell className="h-4 w-4 text-gray-500" />
    };
    return icons[tipo] || icons.default;
  };

  const formatarTempo = (dataString) => {
    const data = new Date(dataString);
    const agora = new Date();
    const diffMs = agora - data;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHoras = Math.floor(diffMins / 60);
    const diffDias = Math.floor(diffHoras / 24);

    if (diffMins < 1) return 'Agora';
    if (diffMins < 60) return `${diffMins}m atrás`;
    if (diffHoras < 24) return `${diffHoras}h atrás`;
    if (diffDias < 7) return `${diffDias}d atrás`;
    return data.toLocaleDateString('pt-BR');
  };

  return (
    <>
      <DropdownMenu>
        <DropdownMenuTrigger asChild>
          <Button variant="ghost" size="sm" className="relative">
            {naoLidas > 0 ? (
              <BellRing className="h-5 w-5" />
            ) : (
              <Bell className="h-5 w-5" />
            )}
            {naoLidas > 0 && (
              <Badge 
                variant="destructive" 
                className="absolute -top-1 -right-1 h-5 w-5 rounded-full p-0 flex items-center justify-center text-xs"
              >
                {naoLidas > 99 ? '99+' : naoLidas}
              </Badge>
            )}
          </Button>
        </DropdownMenuTrigger>
        <DropdownMenuContent align="end" className="w-80">
          <div className="flex items-center justify-between p-2 border-b">
            <h3 className="font-semibold">Notificações</h3>
            {naoLidas > 0 && (
              <Button 
                variant="ghost" 
                size="sm" 
                onClick={marcarTodasLidas}
                disabled={loading}
              >
                <CheckCheck className="h-4 w-4 mr-1" />
                Marcar todas
              </Button>
            )}
          </div>
          
          <ScrollArea className="h-96">
            {notificacoes.length === 0 ? (
              <div className="p-4 text-center text-gray-500">
                <Bell className="h-8 w-8 mx-auto mb-2 opacity-50" />
                <p>Nenhuma notificação</p>
              </div>
            ) : (
              <div className="space-y-1">
                {notificacoes.slice(0, 10).map((notificacao) => (
                  <div
                    key={notificacao.id}
                    className={`p-3 hover:bg-gray-50 cursor-pointer border-l-2 ${
                      !notificacao.lida 
                        ? 'border-l-blue-500 bg-blue-50' 
                        : 'border-l-transparent'
                    }`}
                    onClick={() => !notificacao.lida && marcarComoLida(notificacao.id)}
                  >
                    <div className="flex items-start space-x-3">
                      <div className="flex-shrink-0 mt-1">
                        {getIconeNotificacao(notificacao.tipo)}
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center justify-between">
                          <p className="text-sm font-medium text-gray-900 truncate">
                            {notificacao.titulo}
                          </p>
                          {!notificacao.lida && (
                            <div className="w-2 h-2 bg-blue-500 rounded-full flex-shrink-0"></div>
                          )}
                        </div>
                        <p className="text-xs text-gray-600 mt-1 line-clamp-2">
                          {notificacao.mensagem}
                        </p>
                        <p className="text-xs text-gray-400 mt-1">
                          {formatarTempo(notificacao.data_criacao)}
                        </p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </ScrollArea>
          
          {notificacoes.length > 10 && (
            <div className="p-2 border-t">
              <Button 
                variant="ghost" 
                size="sm" 
                className="w-full"
                onClick={() => setModalAberto(true)}
              >
                Ver todas as notificações
              </Button>
            </div>
          )}
        </DropdownMenuContent>
      </DropdownMenu>

      {/* Modal com todas as notificações */}
      <Dialog open={modalAberto} onOpenChange={setModalAberto}>
        <DialogContent className="sm:max-w-[600px] max-h-[80vh]">
          <DialogHeader>
            <DialogTitle>Todas as Notificações</DialogTitle>
            <DialogDescription>
              Histórico completo de notificações
            </DialogDescription>
          </DialogHeader>
          
          <div className="flex justify-between items-center mb-4">
            <Badge variant="outline">
              {naoLidas} não lidas
            </Badge>
            {naoLidas > 0 && (
              <Button 
                variant="outline" 
                size="sm"
                onClick={marcarTodasLidas}
                disabled={loading}
              >
                <CheckCheck className="h-4 w-4 mr-1" />
                Marcar todas como lidas
              </Button>
            )}
          </div>
          
          <ScrollArea className="h-96">
            <div className="space-y-2">
              {notificacoes.map((notificacao) => (
                <Card 
                  key={notificacao.id}
                  className={`cursor-pointer transition-colors ${
                    !notificacao.lida ? 'border-blue-200 bg-blue-50' : ''
                  }`}
                  onClick={() => !notificacao.lida && marcarComoLida(notificacao.id)}
                >
                  <CardContent className="p-4">
                    <div className="flex items-start space-x-3">
                      <div className="flex-shrink-0 mt-1">
                        {getIconeNotificacao(notificacao.tipo)}
                      </div>
                      <div className="flex-1">
                        <div className="flex items-center justify-between">
                          <h4 className="text-sm font-medium text-gray-900">
                            {notificacao.titulo}
                          </h4>
                          <div className="flex items-center space-x-2">
                            <span className="text-xs text-gray-400">
                              {formatarTempo(notificacao.data_criacao)}
                            </span>
                            {!notificacao.lida && (
                              <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                            )}
                          </div>
                        </div>
                        <p className="text-sm text-gray-600 mt-1">
                          {notificacao.mensagem}
                        </p>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </ScrollArea>
        </DialogContent>
      </Dialog>
    </>
  );
};

export default NotificationCenter;

