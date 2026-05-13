//
//  LoginScreen.swift
//  EasyFriend
//
//  Created by Isabela Hissa Pinto on 12/05/26.
//

import SwiftUI

struct LoginScreen: View {
    @Environment(AuthViewModel.self) private var authViewModel
    @State private var email: String = ""
    @State private var senha: String = ""

    var body: some View {
        VStack(spacing: 24) {
            Spacer()

            VStack(spacing: 4) {
                Text("EasyFriend")
                    .font(.largeTitle)
                    .fontWeight(.semibold)
                Text("Conecte-se")
                    .font(.subheadline)
                    .foregroundStyle(.secondary)
            }

            VStack(spacing: 12) {
                TextField("Email", text: $email)
                    .textFieldStyle(.roundedBorder)
                    .textContentType(.emailAddress)
                    .keyboardType(.emailAddress)
                    .autocapitalization(.none)

                SecureField("Senha", text: $senha)
                    .textFieldStyle(.roundedBorder)
                    .textContentType(.password)

                if let erro = authViewModel.errorMessage {
                    Text(erro)
                        .font(.caption)
                        .foregroundStyle(.red)
                }

                Button {
                    Task {
                        await authViewModel.login(email: email, senha: senha)
                    }
                } label: {
                    if authViewModel.isLoading {
                        ProgressView()
                            .frame(maxWidth: .infinity)
                    } else {
                        Text("Entrar")
                            .frame(maxWidth: .infinity)
                    }
                }
                .buttonStyle(.borderedProminent)
                .disabled(authViewModel.isLoading)

                Button("Criar conta") {
                    // TODO: tela de cadastro (fora do escopo do MVP)
                }
                .font(.caption)
                .foregroundStyle(.secondary)
            }
            .padding(.horizontal)

            Spacer()
            Spacer()
        }
        .padding()
    }
}

#Preview {
    LoginScreen()
        .environment(AuthViewModel())
}
