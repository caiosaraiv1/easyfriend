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

    // Helper para converter os dois Double em um CLLocationCoordinate2D
    // que o MapKit consome. Nao e Codable pq nao vem do backend.
    var coordenada: CLLocationCoordinate2D {
        CLLocationCoordinate2D(latitude: coordenadaLat, longitude: coordenadaLon)
    }

    // Inicial do nome para exibir no marcador do mapa.
    var inicial: String {
        String(usuario.nome.prefix(1)).uppercased()
    }
}
