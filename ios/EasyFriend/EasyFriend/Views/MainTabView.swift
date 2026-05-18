//
//  MainTabView.swift
//  EasyFriend
//
//  Created by Isabela Hissa Pinto on 12/05/26.
//

import SwiftUI

struct MainTabView: View {
    var body: some View {
        TabView {
            RadarScreen()
                .tabItem {
                    Label("Radar", systemImage: "dot.radiowaves.left.and.right")
                }

            AgendaScreen()
                .tabItem {
                    Label("Agenda", systemImage: "calendar")
                }

            PerfilScreen()
                .tabItem {
                    Label("Perfil", systemImage: "person.circle")
                }
        }
    }
}

#Preview {
    MainTabView()
}
