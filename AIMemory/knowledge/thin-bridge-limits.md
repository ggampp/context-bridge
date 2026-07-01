---
title: Thin bridge — o que context-bridge não faz
kind: convention
importance: 10
tags: architecture;scope
source_task: v1.0-design
---

# Limites do thin bridge

Context-bridge **não**:

- Roda `/understand` ou gera grafo UA
- Escreve em `.understand-anything/*.json`
- Substitui dashboard UA ou MCP Engram nativo
- Faz sync bidirecional Engram → grafo

É camada de tradução idempotente: grafo → mem_save; mem_search + grafo → enrich.
