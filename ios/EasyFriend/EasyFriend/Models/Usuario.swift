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

    //campos opcionais
    let idade: Int?
    let idioma: String?
    let idiomas: [String]?
    let interesses: [String]?
    let email: String?

    // Custom decoding para aceitar tanto "usuario_id" quanto "id" do backend.
    // O /auth/me usa "usuario_id"; /radar/matches usa "id" dentro do usuario.
    enum CodingKeys: String, CodingKey {
        case id, usuarioId = "usuario_id"
        case nome, paisOrigem, idade, idioma, idiomas, interesses, email
    }

    init(from decoder: Decoder) throws {
        let c = try decoder.container(keyedBy: CodingKeys.self)
        //tenta "id" primeiro, depois "usuario_id"
        if let i = try? c.decode(Int.self, forKey: .id) {
            self.id = i
        } else {
            self.id = try c.decode(Int.self, forKey: .usuarioId)
        }
        self.nome = try c.decode(String.self, forKey: .nome)
        self.paisOrigem = try c.decode(String.self, forKey: .paisOrigem)
        self.idade = try c.decodeIfPresent(Int.self, forKey: .idade)
        self.idioma = try c.decodeIfPresent(String.self, forKey: .idioma)
        self.idiomas = try c.decodeIfPresent([String].self, forKey: .idiomas)
        self.interesses = try c.decodeIfPresent([String].self, forKey: .interesses)
        self.email = try c.decodeIfPresent(String.self, forKey: .email)
    }

    //init manual MockData
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

    //Helper: retorna a lista de idiomas, normalizando entre os dois formatos.
    var idiomasExibidos: [String] {
        if let lista = idiomas, !lista.isEmpty { return lista }
        if let unico = idioma { return [unico] }
        return []
    }

    func encode(to encoder: Encoder) throws {
        var c = encoder.container(keyedBy: CodingKeys.self)
        try c.encode(id, forKey: .id)
        try c.encode(nome, forKey: .nome)
        try c.encode(paisOrigem, forKey: .paisOrigem)
        try c.encodeIfPresent(idade, forKey: .idade)
        try c.encodeIfPresent(idioma, forKey: .idioma)
        try c.encodeIfPresent(idiomas, forKey: .idiomas)
        try c.encodeIfPresent(interesses, forKey: .interesses)
        try c.encodeIfPresent(email, forKey: .email)
    }
}
