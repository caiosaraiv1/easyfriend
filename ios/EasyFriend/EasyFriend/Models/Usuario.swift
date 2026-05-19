//
//  Usuario.swift
//  EasyFriend
//
//  Created by Isabela Hissa Pinto on 12/05/26.
//

import Foundation

struct Usuario: Codable, Identifiable {
    let id: Int
    let nome: String
    let paisOrigem: String

    let idade: Int?
    let idioma: String?
    let idiomas: [String]?
    let interesses: [String]?
    let email: String?

    private struct AnyKey: CodingKey {
        var stringValue: String
        var intValue: Int? { nil }
        init(stringValue: String) { self.stringValue = stringValue }
        init?(intValue: Int) { return nil }
    }

    init(from decoder: Decoder) throws {
        let c = try decoder.container(keyedBy: AnyKey.self)

        func first<T: Decodable>(_ type: T.Type, _ keys: [String]) -> T? {
            for k in keys {
                let key = AnyKey(stringValue: k)
                if let value = try? c.decode(T.self, forKey: key) {
                    return value
                }
            }
            return nil
        }

        //id pode vir como "id" (radar) ou "usuario_id"/"usuarioId" (auth/me)
        guard let id = first(Int.self, ["id", "usuario_id", "usuarioId"]) else {
            throw DecodingError.keyNotFound(
                AnyKey(stringValue: "id"),
                .init(codingPath: decoder.codingPath,
                      debugDescription: "Nem 'id' nem 'usuario_id' encontrados.")
            )
        }
        self.id = id

        guard let nome = first(String.self, ["nome"]) else {
            throw DecodingError.keyNotFound(
                AnyKey(stringValue: "nome"),
                .init(codingPath: decoder.codingPath,
                      debugDescription: "Campo 'nome' obrigatorio nao encontrado.")
            )
        }
        self.nome = nome

        guard let pais = first(String.self, ["pais_origem", "paisOrigem"]) else {
            throw DecodingError.keyNotFound(
                AnyKey(stringValue: "pais_origem"),
                .init(codingPath: decoder.codingPath,
                      debugDescription: "Campo 'pais_origem' obrigatorio nao encontrado.")
            )
        }
        self.paisOrigem = pais

        self.idade = first(Int.self, ["idade"])
        self.idioma = first(String.self, ["idioma"])
        self.idiomas = first([String].self, ["idiomas"])
        self.interesses = first([String].self, ["interesses"])
        self.email = first(String.self, ["email"])
    }

    init(id: Int, nome: String, paisOrigem: String,
         idade: Int? = nil, idioma: String? = nil,
         idiomas: [String]? = nil, interesses: [String]? = nil,
         email: String? = nil) {
        self.id = id
        self.nome = nome
        self.paisOrigem = paisOrigem
        self.idade = idade
        self.idioma = idioma
        self.idiomas = idiomas
        self.interesses = interesses
        self.email = email
    }

    var idiomasExibidos: [String] {
        if let lista = idiomas, !lista.isEmpty { return lista }
        if let unico = idioma { return [unico] }
        return []
    }

    enum CodingKeys: String, CodingKey {
        case id
        case nome
        case paisOrigem = "pais_origem"
        case idade
        case idioma
        case idiomas
        case interesses
        case email
    }
}
