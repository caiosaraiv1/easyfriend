//
//  ContentView.swift
//  EasyFriend
//
//  Created by Isabela Hissa Pinto on 12/05/26.
//

import SwiftUI

struct ContentView: View {
    // Com @Observable, le do environment pelo tipo da classe.
    @Environment(AuthViewModel.self) private var authViewModel

    var body: some View {
        if authViewModel.isAuthenticated {
            MainTabView()
        } else {
            LoginScreen()
        }
    }
}

#Preview {
    ContentView()
        .environment(AuthViewModel())
}
