document.addEventListener('DOMContentLoaded', function() {
    // 1. Localizar o container da Emoção no form
    const emotionField = document.querySelector('.field-emotion');
    const emotionSelect = document.querySelector('#id_emotion');
    
    if (!emotionField || !emotionSelect) {
        return;
    }

    // 2. Criar a estrutura do painel editorial inteligente
    const container = document.createElement('div');
    container.className = 'editorial-ai-panel';
    container.innerHTML = `
        <div class="editorial-ai-row">
            <input type="text" id="ai-tone-direction" placeholder="Direção espiritual opcional (ex: 'foco na graça', 'tom de diário monástico')" class="vTextField" style="width: 320px; margin-right: 10px; padding: 6px;" />
            <button type="button" id="btn-generate-ai" class="button editorial-ai-button">✨ Gerar Devocional com IA</button>
            <span id="ai-loader" class="ai-pulse-loader" style="display: none; margin-left: 10px; font-weight: bold; color: #447e65;">
                ✨ Sintonizando Claude e inspirando reflexão...
            </span>
        </div>
    `;

    // Inserir logo abaixo do dropdown de emoção
    emotionField.appendChild(container);

    const btnGenerate = document.querySelector('#btn-generate-ai');
    const inputDirection = document.querySelector('#ai-tone-direction');
    const loader = document.querySelector('#ai-loader');

    btnGenerate.addEventListener('click', function(e) {
        e.preventDefault();
        
        // Obter o valor da emoção selecionada
        const emotionVal = emotionSelect.value;
        const emotionText = emotionSelect.options[emotionSelect.selectedIndex].text;
        
        if (!emotionVal) {
            alert('Por favor, selecione uma Emoção no menu suspenso primeiro.');
            emotionSelect.focus();
            return;
        }

        const toneDirection = inputDirection.value.trim();

        // Obter CSRF Token do formulário do admin
        const csrfTokenInput = document.querySelector('[name=csrfmiddlewaretoken]');
        const csrfToken = csrfTokenInput ? csrfTokenInput.value : '';

        // Desativar controles e mostrar carregamento
        btnGenerate.disabled = true;
        emotionSelect.disabled = true;
        inputDirection.disabled = true;
        loader.style.display = 'inline-block';
        btnGenerate.style.opacity = '0.6';

        // Fazer chamada ao backend com credenciais da sessão ativa
        fetch('/api/devotional/editorial/generate/', {
            method: 'POST',
            credentials: 'same-origin',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify({
                emotion_slug: getSlugFromOptionText(emotionText),
                tone_or_direction: toneDirection
            })
        })
        .then(response => {
            if (!response.ok) {
                return response.json().then(err => { throw err; });
            }
            return response.json();
        })
        .then(data => {
            // Preencher os campos do formulário no admin
            fillField('#id_title', data.title);
            fillField('#id_scripture_reference', data.scripture_reference);
            fillField('#id_scripture_text', data.scripture_text);
            fillField('#id_reflection', data.reflection);
            fillField('#id_prayer', data.prayer);
            fillField('#id_share_quote', data.share_quote);
            fillField('#id_emotional_theme', data.emotional_theme);
            
            // Marcar gerado por IA como True, e curado por humano como False (obriga curadoria manual)
            setCheckbox('#id_ai_generated', true);
            setCheckbox('#id_reviewed_by_human', false);
            
            // Notificação sutil
            showSuccessNotification('Devocional gerado com sucesso! Por favor, revise os textos e marque "Revisado por Humano" antes de salvar.');
        })
        .catch(error => {
            console.error('Falha na geração com IA:', error);
            const errMsg = error.message || 'Erro de rede ou permissão insuficiente.';
            alert(`Falha ao gerar devocional com IA: ${errMsg}\n\nSeus campos atuais não foram alterados.`);
        })
        .finally(() => {
            // Reativar controles
            btnGenerate.disabled = false;
            emotionSelect.disabled = false;
            inputDirection.disabled = false;
            loader.style.display = 'none';
            btnGenerate.style.opacity = '1';
        });
    });

    // Helpers
    function getSlugFromOptionText(text) {
        return text.toLowerCase()
            .normalize("NFD")
            .replace(/[\u0300-\u036f]/g, "")
            .replace(/[^a-z0-9]+/g, '-')
            .replace(/(^-|-$)+/g, '');
    }

    function fillField(selector, value) {
        const field = document.querySelector(selector);
        if (field && value) {
            field.value = value;
            // Disparar evento de input caso haja ouvintes reativos
            field.dispatchEvent(new Event('input', { bubbles: true }));
        }
    }

    function setCheckbox(selector, checked) {
        const checkbox = document.querySelector(selector);
        if (checkbox) {
            checkbox.checked = checked;
            checkbox.dispatchEvent(new Event('change', { bubbles: true }));
        }
    }

    function showSuccessNotification(message) {
        // Criar um pequeno banner de notificação temporário
        const banner = document.createElement('div');
        banner.className = 'editorial-ai-notification';
        banner.innerHTML = `✨ ${message}`;
        document.body.appendChild(banner);
        
        setTimeout(() => {
            banner.classList.add('fade-out');
            setTimeout(() => banner.remove(), 1000);
        }, 6000);
    }
});
