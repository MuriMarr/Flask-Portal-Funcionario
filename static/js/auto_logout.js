/**
 * Auto Logout - Faz logout correto quando o usuário fecha a página
 * Coordena com o heartbeat para manter a sessão viva
 */
(function () {
    const beaconUrl = window.LOGOUT_URL || '/auth/logout_beacon';
    
    // Faz logout quando a página é fechada/descarregada (não apenas navegado)
    window.addEventListener("unload", function (event) {
        // Usa sendBeacon para garantir que seja enviado mesmo durante unload
        try {
            navigator.sendBeacon(beaconUrl, JSON.stringify({ action: 'logout' }));
        } catch (e) {
            console.debug("Falha ao enviar beacon de logout", e);
        }
    });

    // Também tenta logout no pagehide para maior compatibilidade
    window.addEventListener("pagehide", function (event) {
        // Apenas logout se a página não está sendo mantida em cache (bfcache)
        if (event.persisted === false) {
            try {
                navigator.sendBeacon(beaconUrl, JSON.stringify({ action: 'logout' }));
            } catch (e) {
                console.debug("Falha no sendBeacon de logout", e);
            }
        }
    });

    // Detecta se o usuário foi deslogado de outra aba/janela (sincronização de sessão)
    document.addEventListener('visibilitychange', function() {
        if (document.hidden === false) {
            // Página voltou ao foco, verifica se ainda está autenticado
            fetch('/auth/refresh_session', {
                method: 'POST',
                credentials: 'same-origin'
            })
            .then(response => {
                if (response.status === 401) {
                    // Deslogado, redireciona para login
                    window.location.href = '/auth/login';
                }
            })
            .catch(() => {
                // Erro na verificação, pode ser perda de conexão
                console.debug('Não foi possível verificar sessão');
            });
        }
    });
})();
