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
    let idade: Int
    let paisOrigem: String
    let idiomas: [String]
    let interesses: [String]
    let email: String?
}
