//
//  Match.swift
//  EasyFriend
//
//  Created by Isabela Hissa Pinto on 12/05/26.
//


import Foundation
import CoreLocation

struct Match: Codable, Identifiable {
    let id: Int
    let usuario: Usuario
    let coordenadaLat: Double
    let coordenadaLon: Double
    let raioPrivacidadeMetros: Double
    let distanciaKm: Double
    let criadoEm: Date

    var coordenada: CLLocationCoordinate2D {
        CLLocationCoordinate2D(latitude: coordenadaLat, longitude: coordenadaLon)
    }

    var inicial: String {
        String(usuario.nome.prefix(1)).uppercased()
    }

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

        guard let id = first(Int.self, ["id"]) else {
            throw DecodingError.keyNotFound(
                AnyKey(stringValue: "id"),
                .init(codingPath: decoder.codingPath,
                      debugDescription: "Match sem 'id'.")
            )
        }
        self.id = id

        guard let usuario = first(Usuario.self, ["usuario"]) else {
            throw DecodingError.keyNotFound(
                AnyKey(stringValue: "usuario"),
                .init(codingPath: decoder.codingPath,
                      debugDescription: "Match sem 'usuario'.")
            )
        }
        self.usuario = usuario

        self.coordenadaLat = first(Double.self, ["coordenada_lat", "coordenadaLat"]) ?? 0
        self.coordenadaLon = first(Double.self, ["coordenada_lon", "coordenadaLon"]) ?? 0
        self.raioPrivacidadeMetros = first(Double.self, ["raio_privacidade_metros", "raioPrivacidadeMetros"]) ?? 300
        self.distanciaKm = first(Double.self, ["distancia_km", "distanciaKm"]) ?? 0

        if let dataStr = first(String.self, ["criado_em", "criadoEm"]) {
            self.criadoEm = Match.parseDate(dataStr) ?? Date()
        } else {
            self.criadoEm = Date()
        }
    }

    init(id: Int, usuario: Usuario,
         coordenadaLat: Double, coordenadaLon: Double,
         raioPrivacidadeMetros: Double, distanciaKm: Double,
         criadoEm: Date) {
        self.id = id
        self.usuario = usuario
        self.coordenadaLat = coordenadaLat
        self.coordenadaLon = coordenadaLon
        self.raioPrivacidadeMetros = raioPrivacidadeMetros
        self.distanciaKm = distanciaKm
        self.criadoEm = criadoEm
    }

    private static func parseDate(_ string: String) -> Date? {
        let formatter = DateFormatter()
        formatter.locale = Locale(identifier: "en_US_POSIX")
        formatter.timeZone = TimeZone(secondsFromGMT: 0)

        let formatos = [
            "yyyy-MM-dd'T'HH:mm:ss.SSSSSS",
            "yyyy-MM-dd'T'HH:mm:ss.SSSSSSXXXXX",
            "yyyy-MM-dd'T'HH:mm:ss.SSS",
            "yyyy-MM-dd'T'HH:mm:ss.SSSXXXXX",
            "yyyy-MM-dd'T'HH:mm:ss",
            "yyyy-MM-dd'T'HH:mm:ssXXXXX",
        ]
        for f in formatos {
            formatter.dateFormat = f
            if let d = formatter.date(from: string) { return d }
        }
        let iso = ISO8601DateFormatter()
        iso.formatOptions = [.withInternetDateTime, .withFractionalSeconds]
        if let d = iso.date(from: string) { return d }
        iso.formatOptions = [.withInternetDateTime]
        return iso.date(from: string)
    }
}
