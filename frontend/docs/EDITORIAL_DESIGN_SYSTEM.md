# CAPIO Design System
**A Arquitetura da Gramática do Silêncio**

Este documento detalha o sistema de design construído para a CAPIO, focado em transmitir uma identidade visual de silêncio, contemplação, papel impresso, e reverência.

## 1. Princípios
- **Tecnologia Oculta:** O aplicativo não deve se assemelhar a um SaaS genérico ou um aplicativo de feed moderno cheio de sombras e interações agressivas.
- **A Palavra no Centro:** O layout trabalha com muito respiro (whitespace) e escalas rigorosas para que o usuário "descanse" na tela.
- **Papel sobre Papel:** Não usamos brancos puros chapados contra o fundo. Trabalhamos texturas sutis (Background Off-White `#F8F7F4` vs Surface `#FCFBF8`) unidas por bordas quase invisíveis (`#E6E1D8`).

## 2. Tipografia e Cores (Tokens)
Em vez de definir estilos hardcoded pelo código (`text-[10px]`, `text-[#A68463]`), usamos tipografia atrelada aos tokens:
- **`.editorial-title`**: Para títulos principais (ex: Devocional, "O coração do texto").
- **`.editorial-subtitle`**: Textos descritivos que complementam o título.
- **`.editorial-label`**: Para marcações como "COMPREENDENDO ESTA PASSAGEM" (Uppercase com tracking-widest).
- **`.editorial-body`**: O texto de foco principal (Reflexões, Bíblia). Usa `Lora` e espaçamento matemático de entrelinhas.
- **Cores principais**: `bg-background`, `bg-surface`, `border-border`, `text-brand`, `text-accent`.

## 3. Escala de Espaçamento Modular
A CAPIO aboliu valores de margin soltos. Usamos:
- `xs` (8px)
- `sm` (16px)
- `md` (24px)
- `lg` (32px)
- `xl` (48px)
- `2xl` (64px)

Use utilitários Tailwind em conjunto com esses tokens: `mt-xl`, `space-y-md`, `gap-sm`, `py-2xl`.

## 4. Componentes do Design System (`src/components/design-system/editorial`)

### `EditorialContainer`
O invólucro (shell) global. Toda página da CAPIO deve renderizar seu conteúdo principal dentro dele.
Ele garante que Safe Areas (PWA `env(safe-area-inset-*)`), centralização e `max-w-4xl` sejam aplicados uniformemente.

### `EditorialSection`
Uma divisão principal dentro do Container. Ajuda a definir espaços verticais (`py-xl`) consistentes ao trocar de contexto.

### `EditorialCard`
O "papel" final onde o texto reside. Padroniza borda, surface color, e `border-radius`, abolindo variações de Card customizadas.

### `EditorialDivider`
Substitui todas as tags `<hr>` manuais. Possui variações de estilo: `line`, `short`, `dot`.

### `EditorialNavigation`
Um controlador flexível para links de "Próximo / Anterior" (ex: Capítulos Bíblicos), que resolve quebras feias no mobile ao usar text-truncation e grid equilibrado.

### `EditorialActionRow`
Controla os ícones e rótulos de ações globais (Copiar, Compartilhar, Salvar). Padroniza alturas, espaçamentos, e um grid seguro de 3 colunas fluídas.

## 5. Exemplo de Composição

```jsx
import {
  EditorialContainer,
  EditorialSection,
  EditorialCard,
  EditorialTitle,
  EditorialLabel,
  EditorialDivider
} from '../components/design-system/editorial';

export default function ExemploPage() {
  return (
    <EditorialContainer>
      <EditorialSection>
        <EditorialCard>
          
          <EditorialLabel className="text-center mb-md">
            Um rótulo no topo
          </EditorialLabel>
          
          <EditorialTitle className="text-center mb-xl">
            Tudo segue o padrão
          </EditorialTitle>

          <EditorialDivider variant="short" />
          
          <p className="editorial-body">
            Este texto terá automaticamente o alinhamento, fonte e entrelinhas aprovados pela Gramática do Silêncio.
          </p>
          
        </EditorialCard>
      </EditorialSection>
    </EditorialContainer>
  );
}
```

## 6. Regra Inegociável
Nenhuma tela deve conter estilos estruturais ou de calibração fina hardcoded (como `pt-[60px]`, `text-[#000]`, ou `rounded-3xl`). Todo espaçamento e cor devem fluir do Design System. Estilos estritamente únicos para uma lógica visual (ex: posicionar um highlight interativo) podem ser declarados no componente afetado.
