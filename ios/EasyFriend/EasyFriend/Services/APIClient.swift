//
//  APIClient.swift
//  EasyFriend
//
//  Created by Isabela Hissa Pinto on 12/05/26.
//


import Foundation

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

    //trocar pra false dps
    private let USE_MOCK = true

    private let baseURL = "http://127.0.0.1:8000"

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

    // MARK: - GET

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

    // MARK: - POST JSON

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

    // MARK: - POST form-data (para /auth/login)

    /// Envia POST com Content-Type: application/x-www-form-urlencoded.
    /// Necessario porque o FastAPI usa OAuth2PasswordRequestForm no /auth/login,
    /// que so aceita form-data (nao JSON).
    func postFormData<T: Decodable>(_ path: String, fields: [String: String]) async throws -> T {
        if USE_MOCK { return try mockResponse(for: path) }

        guard let url = URL(string: baseURL + path) else { throw APIError.badURL }
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/x-www-form-urlencoded", forHTTPHeaderField: "Content-Type")

        // cdifica os campos no formato chave=valor&chave=valor com URL encoding
        let bodyString = fields.map { (key, value) -> String in
            let encodedKey = key.addingPercentEncoding(withAllowedCharacters: .urlQueryAllowed) ?? key
            let encodedValue = value.addingPercentEncoding(withAllowedCharacters: .urlQueryAllowed) ?? value
            return "\(encodedKey)=\(encodedValue)"
        }.joined(separator: "&")

        request.httpBody = bodyString.data(using: .utf8)

        let (data, response) = try await URLSession.shared.data(for: request)
        try validate(response: response)
        do {
            return try decoder.decode(T.self, from: data)
        } catch {
            throw APIError.decodingFailed(error.localizedDescription)
        }
    }

    // MARK: - PATCH (para /apadrinhamento/{id}/aceitar)

    func patch<T: Decodable>(_ path: String) async throws -> T {
        if USE_MOCK { return try mockResponse(for: path) }

        guard let url = URL(string: baseURL + path) else { throw APIError.badURL }
        var request = URLRequest(url: url)
        request.httpMethod = "PATCH"
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

    // MARK: - Mocks

    private func mockResponse<T: Decodable>(for path: String) throws -> T {
        Thread.sleep(forTimeInterval: 0.4)

        if path.hasPrefix("/radar/matches") {
            let criterio = extractParam("criterio", from: path) ?? "proximidade"
            let matches = MockData.matches(criterio: criterio)
            return matches as! T
        }
        if path.hasPrefix("/agenda/eventos") {
            let valor = extractParam("valor", from: path)
            let eventos = MockData.eventos(tipoFiltro: valor)
            return eventos as! T
        }
        if path.hasPrefix("/auth/login") {
            let resp = LoginResponse(
                accessToken: "mock-jwt-token-12345",
                tokenType: "bearer",
                usuarioId: 1,
                nome: "Isabela Hissa"
            )
            return resp as! T
        }
        if path.hasPrefix("/auth/me") {
            return MockData.usuarioAtual as! T
        }
        if path.hasPrefix("/apadrinhamento/solicitar") {
            let resp = ApadrinhamentoResponse(id: 99, status: "pendente")
            return resp as! T
        }
        throw APIError.badURL
    }

    private func extractParam(_ key: String, from path: String) -> String? {
        guard let comps = URLComponents(string: path) else { return nil }
        return comps.queryItems?.first(where: { $0.name == key })?.value
    }
}

// MARK: - Respostas tipadas

struct LoginResponse: Codable {
    let accessToken: String
    let tokenType: String
    let usuarioId: Int
    let nome: String
}

struct ApadrinhamentoResponse: Codable {
    let id: Int
    let status: String
}
