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
    @Environment(AuthViewModel.self) private var authViewModel
    @State private var pedidoEnviado = false
    @State private var enviando = false
    @State private var erroPedido: String?

    var body: some View {
        NavigationStack {
            VStack(spacing: 20) {
                Circle()
                    .fill(Color.blue.opacity(0.2))
                    .frame(width: 100, height: 100)
                    .overlay(
                        Text(match.inicial)
                            .font(.system(size: 40, weight: .semibold))
                            .foregroundStyle(.blue)
                    )

                VStack(spacing: 4) {
                    Text(nomeComIdade)
                        .font(.title2)
                        .fontWeight(.semibold)
                    Text("\(match.usuario.paisOrigem) · ~\(String(format: "%.1f", match.distanciaKm)) km de você")
                        .font(.subheadline)
                        .foregroundStyle(.secondary)
                }

                Divider()

                VStack(alignment: .leading, spacing: 12) {
                    if !match.usuario.idiomasExibidos.isEmpty {
                        secao(titulo: "IDIOMAS", items: match.usuario.idiomasExibidos)
                    }
                    if let interesses = match.usuario.interesses, !interesses.isEmpty {
                        secao(titulo: "INTERESSES", items: interesses)
                    }
                }
                .frame(maxWidth: .infinity, alignment: .leading)
                .padding(.horizontal)

                Spacer()

                if pedidoEnviado {
                    Label("Pedido enviado!", systemImage: "checkmark.circle.fill")
                        .foregroundStyle(.green)
                        .padding()
                } else {
                    VStack(spacing: 8) {
                        if let erro = erroPedido {
                            Text(erro)
                                .font(.caption)
                                .foregroundStyle(.red)
                                .multilineTextAlignment(.center)
                                .padding(.horizontal)
                        }

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

    private var nomeComIdade: String {
        if let idade = match.usuario.idade {
            return "\(match.usuario.nome), \(idade)"
        }
        return match.usuario.nome
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
        erroPedido = nil
        defer { enviando = false }

        // Estrutura esperada pelo backend (app/routes/apadrinhamento.py):
        //   { "padrinho_id": int, "afilhado_id": int }
        struct SolicitacaoBody: Codable {
            let padrinhoId: Int
            let afilhadoId: Int
        }

        guard let usuarioAtualId = authViewModel.usuarioAtual?.id else {
            erroPedido = "Voce precisa estar logado para fazer pedidos."
            return
        }

        let body = SolicitacaoBody(
            padrinhoId: match.usuario.id,
            afilhadoId: usuarioAtualId
        )

        do {
            let _: ApadrinhamentoResponse = try await APIClient.shared.post(
                "/apadrinhamento/solicitar",
                body: body
            )
            pedidoEnviado = true
        } catch {
            erroPedido = "Falha ao enviar: \(error.localizedDescription)"
        }
    }
}

#Preview {
    DetalheMatchScreen(match: MockData.matches(criterio: "proximidade")[0])
        .environment(AuthViewModel())
}
