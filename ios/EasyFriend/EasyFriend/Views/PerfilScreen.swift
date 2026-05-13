//
//  PerfilScreen.swift
//  EasyFriend
//
//  Created by Isabela Hissa Pinto on 12/05/26.
//

import SwiftUI

struct PerfilScreen: View {
    @Environment(AuthViewModel.self) private var authViewModel

    var body: some View {
        NavigationStack {
            List {
                Section {
                    VStack(spacing: 8) {
                        Circle()
                            .fill(Color.blue.opacity(0.2))
                            .frame(width: 80, height: 80)
                            .overlay(
                                Text(inicialUsuario)
                                    .font(.system(size: 32, weight: .semibold))
                                    .foregroundStyle(.blue)
                            )
                        Text(authViewModel.usuarioAtual?.nome ?? "Usuário")
                            .font(.title3)
                            .fontWeight(.semibold)
                        Text(authViewModel.usuarioAtual?.paisOrigem ?? "")
                            .font(.subheadline)
                            .foregroundStyle(.secondary)
                    }
                    .frame(maxWidth: .infinity)
                    .listRowBackground(Color.clear)
                }

                Section {
                    linha(icone: "person.crop.circle", titulo: "Editar perfil")
                    HStack {
                        Label("Apadrinhamento", systemImage: "person.2")
                        Spacer()
                        Text("2 ativos")
                            .font(.caption)
                            .padding(.horizontal, 8)
                            .padding(.vertical, 3)
                            .background(Color.green.opacity(0.2))
                            .foregroundStyle(Color.green)
                            .clipShape(Capsule())
                    }
                    linha(icone: "globe", titulo: "Idiomas")
                    linha(icone: "bell", titulo: "Notificações")
                }

                Section {
                    Button(role: .destructive) {
                        authViewModel.logout()
                    } label: {
                        Label("Sair", systemImage: "rectangle.portrait.and.arrow.right")
                    }
                }
            }
            .navigationTitle("Perfil")
        }
    }

    private var inicialUsuario: String {
        guard let nome = authViewModel.usuarioAtual?.nome,
              let primeira = nome.first else { return "?" }
        return String(primeira).uppercased()
    }

    private func linha(icone: String, titulo: String) -> some View {
        HStack {
            Label(titulo, systemImage: icone)
            Spacer()
            Image(systemName: "chevron.right")
                .font(.caption)
                .foregroundStyle(.tertiary)
        }
    }
}

#Preview {
    PerfilScreen()
        .environment(AuthViewModel())
}
