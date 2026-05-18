//
//  DetalhesMatchScreen.swift
//  EasyFriend
//
//  Created by Isabela Hissa Pinto on 12/05/26.
//

import SwiftUI

struct DetalheMatchScreen: View {
    let match: Match
    @Environment(\.dismiss) private var dismiss
    @State private var pedidoEnviado = false
    @State private var enviando = false

    var body: some View {
        NavigationStack {
            VStack(spacing: 20) {
                // Avatar grande
                Circle()
                    .fill(Color.blue.opacity(0.2))
                    .frame(width: 100, height: 100)
                    .overlay(
                        Text(match.inicial)
                            .font(.system(size: 40, weight: .semibold))
                            .foregroundStyle(.blue)
                    )

                VStack(spacing: 4) {
                    Text("\(match.usuario.nome), \(match.usuario.idade)")
                        .font(.title2)
                        .fontWeight(.semibold)
                    Text("\(match.usuario.paisOrigem) · ~\(String(format: "%.1f", match.distanciaKm)) km de você")
                        .font(.subheadline)
                        .foregroundStyle(.secondary)
                }

                Divider()

                VStack(alignment: .leading, spacing: 12) {
                    secao(titulo: "IDIOMAS", items: match.usuario.idiomas)
                    secao(titulo: "INTERESSES", items: match.usuario.interesses)
                }
                .frame(maxWidth: .infinity, alignment: .leading)
                .padding(.horizontal)

                Spacer()

                // Acao principal: pedir apadrinhamento
                if pedidoEnviado {
                    Label("Pedido enviado!", systemImage: "checkmark.circle.fill")
                        .foregroundStyle(.green)
                        .padding()
                } else {
                    Button {
                        Task { await pedirApadrinhamento() }
                    } label: {
                        if enviando {
                            ProgressView()
                                .frame(maxWidth: .infinity)
                        } else {
                            Text("Pedir apadrinhamento")
                                .frame(maxWidth: .infinity)
                        }
                    }
                    .buttonStyle(.borderedProminent)
                    .disabled(enviando)
                    .padding(.horizontal)
                }
            }
            .padding(.vertical)
            .navigationTitle("Perfil")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .topBarLeading) {
                    Button("Fechar") { dismiss() }
                }
            }
        }
    }

    private func secao(titulo: String, items: [String]) -> some View {
        VStack(alignment: .leading, spacing: 6) {
            Text(titulo)
                .font(.caption)
                .foregroundStyle(.tertiary)
            HStack {
                ForEach(items, id: \.self) { item in
                    Text(item)
                        .font(.caption)
                        .padding(.horizontal, 10)
                        .padding(.vertical, 4)
                        .background(Color.gray.opacity(0.15))
                        .clipShape(Capsule())
                }
            }
        }
    }

    private func pedirApadrinhamento() async {
        enviando = true
        defer { enviando = false }

        // Endpoint do backend: POST /apadrinhamento/solicitar
        // No backend, isso dispara o Observer (PushNotifier, EmailNotifier).
        // Por enquanto, simula sucesso apos delay.
        try? await Task.sleep(nanoseconds: 600_000_000)
        pedidoEnviado = true
    }
}

#Preview {
    DetalheMatchScreen(match: MockData.matches(criterio: "proximidade")[0])
}
