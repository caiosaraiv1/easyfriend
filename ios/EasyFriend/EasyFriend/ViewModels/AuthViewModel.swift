//
//  AuthViewModel.swift
//  EasyFriend
//
//  Created by Isabela Hissa Pinto on 12/05/26.
//

import Foundation

@MainActor
@Observable
class AuthViewModel {
    var isAuthenticated: Bool = false
    var usuarioAtual: Usuario?
    var isLoading: Bool = false
    var errorMessage: String?

    init() {
        if AuthService.shared.isLoggedIn {
            isAuthenticated = true
            Task { await carregarUsuarioAtual() }
        }
    }

    func login(email: String, senha: String) async {
        isLoading = true
        errorMessage = nil
        defer { isLoading = false }

        struct LoginRequest: Codable {
            let email: String
            let senha: String
        }

        do {
            let resp: LoginResponse = try await APIClient.shared.post(
                "/auth/login",
                body: LoginRequest(email: email, senha: senha)
            )
            AuthService.shared.token = resp.accessToken
            isAuthenticated = true
            await carregarUsuarioAtual()
        } catch {
            errorMessage = error.localizedDescription
        }
    }

    func logout() {
        AuthService.shared.logout()
        isAuthenticated = false
        usuarioAtual = nil
    }

    private func carregarUsuarioAtual() async {
        do {
            usuarioAtual = try await APIClient.shared.get("/usuarios/me")
        } catch {
            print("Falha ao carregar usuario atual: \(error)")
        }
    }
}
