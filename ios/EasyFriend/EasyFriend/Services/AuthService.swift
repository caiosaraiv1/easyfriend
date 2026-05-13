//
//  AuthService.swift
//  EasyFriend
//
//  Created by Isabela Hissa Pinto on 12/05/26.
//


import Foundation

class AuthService {
    static let shared = AuthService()
    private init() {}

    private let tokenKey = "easyfriend.jwt"

    var token: String? {
        get { UserDefaults.standard.string(forKey: tokenKey) }
        set {
            if let value = newValue {
                UserDefaults.standard.set(value, forKey: tokenKey)
            } else {
                UserDefaults.standard.removeObject(forKey: tokenKey)
            }
        }
    }

    var isLoggedIn: Bool { token != nil }

    func logout() {
        token = nil
    }
}
