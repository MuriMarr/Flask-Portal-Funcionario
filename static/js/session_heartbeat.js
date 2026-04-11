/**
 * Session Heartbeat - Mantém a sessão ativa enviando ping periódico ao servidor
 * Renova a sessão a cada 5 minutos enquanto o usuário está na página
 */
(function () {
    const HEARTBEAT_INTERVAL = 5 * 60 * 1000; // 5 minutos em milisegundos
    const HEARTBEAT_URL = '/auth/refresh_session';
    let heartbeatTimer = null;
    let lastActivityTime = Date.now();
    let isUserActive = true;

    // Detecta atividade do usuário
    function resetActivityTimer() {
        lastActivityTime = Date.now();
        isUserActive = true;
    }

    // Listeners para atividade do usuário
    document.addEventListener('mousedown', resetActivityTimer);
    document.addEventListener('keydown', resetActivityTimer);
    document.addEventListener('scroll', resetActivityTimer);
    document.addEventListener('touchstart', resetActivityTimer);
    document.addEventListener('click', resetActivityTimer);

    // Função para enviar heartbeat ao servidor
    function sendHeartbeat() {
        if (!isUserActive) {
            clearInterval(heartbeatTimer);
            return;
        }

        fetch(HEARTBEAT_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            credentials: 'same-origin',
            body: JSON.stringify({
                timestamp: new Date().toISOString()
            })
        })
        .then(response => {
            if (response.status === 401) {
                // Usuário foi deslogado no servidor
                console.warn('Sessão expirada no servidor');
                window.location.href = '/auth/login';
            }
        })
        .catch(error => {
            console.debug('Erro ao enviar heartbeat:', error);
        });
    }

    // Inicia o heartbeat quando a página está pronta
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function () {
            heartbeatTimer = setInterval(sendHeartbeat, HEARTBEAT_INTERVAL);
            // Enviar heartbeat imediatamente após carregar
            sendHeartbeat();
        });
    } else {
        heartbeatTimer = setInterval(sendHeartbeat, HEARTBEAT_INTERVAL);
        sendHeartbeat();
    }

    // Para o heartbeat quando a página perde foco por muito tempo
    let focusTimer = null;
    window.addEventListener('blur', function () {
        isUserActive = false;
    });
    
    window.addEventListener('focus', function () {
        isUserActive = true;
        resetActivityTimer();
        // Enviar heartbeat imediatamente ao retomar foco
        sendHeartbeat();
    });
})();
