//
//  APIClient.swift
//  EasyFriend
//
//  Created by Isabela Hissa Pinto on 12/05/26.
//


import Foundation
import CoreLocation

enum APIError: Error, LocalizedError {
    case badURL
    case requestFailed(Int)
    case decodingFailed(String)
    case unauthorized

    var errorDescription: String? {
        switch self {
        case .badURL: return "URL invalida"
        case .requestFailed(let code): return "Falha HTTP \(code)"
        case .decodingFailed(let msg): return "Falha ao decodificar: \(msg)"
        case .unauthorized: return "Nao autorizado. Faca login novamente."
        }
    }
}

class APIClient {
    static let shared = APIClient()
    private init() {}

    // Troque para false quando o backend estiver pronto e rodando.
    private let USE_MOCK = true

    private let baseURL = "http://127.0.0.1:8000"

    // JSONDecoder configurado para o backend FastAPI:
    // - converte snake_case (backend) para camelCase (Swift) automaticamente
    // - decodifica datas ISO 8601 (formato padrao Python/JSON)
    private var decoder: JSONDecoder {
        let d = JSONDecoder()
        d.keyDecodingStrategy = .convertFromSnakeCase
        d.dateDecodingStrategy = .iso8601
        return d
    }

    private var encoder: JSONEncoder {
        let e = JSONEncoder()
        e.keyEncodingStrategy = .convertToSnakeCase
        e.dateEncodingStrategy = .iso8601
        return e
    }

    // MARK: - GET generico

    func get<T: Decodable>(_ path: String) async throws -> T {
        if USE_MOCK { return try mockResponse(for: path) }

        guard let url = URL(string: baseURL + path) else { throw APIError.badURL }
        var request = URLRequest(url: url)
        addAuthHeader(to: &request)

        let (data, response) = try await URLSession.shared.data(for: request)
        try validate(response: response)
        do {
            return try decoder.decode(T.self, from: data)
        } catch {
            throw APIError.decodingFailed(error.localizedDescription)
        }
    }

    // MARK: - POST generico

    func post<T: Decodable, B: Encodable>(_ path: String, body: B) async throws -> T {
        if USE_MOCK { return try mockResponse(for: path) }

        guard let url = URL(string: baseURL + path) else { throw APIError.badURL }
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.httpBody = try encoder.encode(body)
        addAuthHeader(to: &request)

        let (data, response) = try await URLSession.shared.data(for: request)
        try validate(response: response)
        do {
            return try decoder.decode(T.self, from: data)
        } catch {
            throw APIError.decodingFailed(error.localizedDescription)
        }
    }

    // MARK: - Helpers privados

    private func addAuthHeader(to request: inout URLRequest) {
        if let token = AuthService.shared.token {
            request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        }
    }

    private func validate(response: URLResponse) throws {
        guard let http = response as? HTTPURLResponse else { return }
        if http.statusCode == 401 { throw APIError.unauthorized }
        if !(200...299).contains(http.statusCode) {
            throw APIError.requestFailed(http.statusCode)
        }
    }

    // MARK: - Mocks (remova quando integrar com o backend real)

    private func mockResponse<T: Decodable>(for path: String) throws -> T {
        // Simula latencia de rede de 400ms para parecer real
        Thread.sleep(forTimeInterval: 0.4)

        if path.hasPrefix("/radar/matches") {
            let criterio = extractParam("criterio", from: path) ?? "proximidade"
            let matches = MockData.matches(criterio: criterio)
            // swiftlint:disable:next force_cast
            return matches as! T
        }

        if path.hasPrefix("/agenda/eventos") {
            let tipo = extractParam("valor", from: path)
            let eventos = MockData.eventos(tipoFiltro: tipo)
            // swiftlint:disable:next force_cast
            return eventos as! T
        }

        if path.hasPrefix("/auth/login") {
            let resp = LoginResponse(accessToken: "mock-jwt-token-12345")
            // swiftlint:disable:next force_cast
            return resp as! T
        }

        if path.hasPrefix("/usuarios/me") {
            // swiftlint:disable:next force_cast
            return MockData.usuarioAtual as! T
        }

        throw APIError.badURL
    }

    private func extractParam(_ key: String, from path: String) -> String? {
        guard let comps = URLComponents(string: path) else { return nil }
        return comps.queryItems?.first(where: { $0.name == key })?.value
    }
}

// MARK: - Resposta de login

struct LoginResponse: Codable {
    let accessToken: String
}
