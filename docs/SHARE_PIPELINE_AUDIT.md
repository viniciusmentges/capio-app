# Auditoria e Solução do Pipeline de Compartilhamento (CAPIO)

## Causa Raiz Identificada
Anteriormente, a geração de cards de compartilhamento apresentava falhas intermitentes (imagens em branco, fontes incorretas ou corte de layout) especialmente em dispositivos móveis (iOS Safari e Android Webview).

A causa raiz era a **captura assíncrona prematura do DOM**. A biblioteca `html-to-image` iniciava a serialização do nó DOM no canvas antes que:
1. As fontes web animadas ou dinâmicas (`document.fonts`) tivessem concluído o carregamento.
2. As tags `<img>` internas (logos, texturas) estivessem completamente decodificadas na memória de vídeo pela engine do navegador.
3. O layout recalculado da flexbox tivesse sido efetivamente pintado na tela.

## Solução Implementada em `ShareCardActions.jsx`

### 1. Espera Determinística de Recursos (`waitForResources`)
Antes de acionar `htmlToImage.toJpeg()`, o pipeline aguarda explicitamente:
- `await document.fonts.ready`: Garante a disponibilidade das métricas exatas tipográficas.
- `img.decode()`: Força a decodificação de todas as imagens filhas na GPU.
- Duplo `requestAnimationFrame`: Garante que o navegador completou o ciclo de reflow e repaint.

### 2. Validação Física do Blob (`validateImageExport`)
Para impedir o compartilhamento ou download de arquivos corrompidos:
- Verificação do tamanho do Blob exportado (`size >= 5000 bytes`).
- Verificação física das dimensões renderizadas (`naturalWidth >= 100px` e `naturalHeight >= 100px`).

### 3. Feedback Visual e Resiliência
- Estado `isExporting` refletido no botão (`"Gerando imagem..."`).
- Configurações otimizadas com `pixelRatio: 3`, `quality: 0.95` e `cacheBust: true`.
- Fallback automático para salvar na galeria caso a API nativa `navigator.share` falhe ou não suporte arquivos.
