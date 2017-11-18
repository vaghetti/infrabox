import APIService from '../services/APIService'
import NotificationService from '../services/NotificationService'
import Notification from '../models/Notification'
import store from '../store'

export default class Project {
    constructor (name, id, type) {
        this.name = name
        this.id = id
        this.builds = []
        this.commits = []
        this.state = 'finished'
        this.type = type
        this.secrets = null
        this.collaborators = null
        this.tokens = null
    }

    isGit () {
        return this.type === 'github' || this.type === 'gerrit'
    }

    getActiveBuilds () {
        const builds = []
        for (let b of this.builds) {
            if (b.state === 'running') {
                builds.push(b)
            }
        }

        return builds
    }

    getBuild (number, restartCounter) {
        const b = this._getBuild(number, restartCounter)

        if (b) {
            return new Promise((resolve) => { resolve(b) })
        }

        return APIService.get(`project/${this.id}/build/${number}/${restartCounter}`)
            .then((jobs) => {
                this._addJobs(jobs)
                return this._getBuild(number, restartCounter)
            })
    }

    removeCollaborator (co) {
        return APIService.delete(`project/${this.id}/collaborators/${co.id}`)
            .then((response) => {
                NotificationService.$emit('NOTIFICATION', new Notification(response, 'done'))
                this._reloadCollaborators()
            })
    }

    deleteToken (id) {
        delete APIService.delete(`project/${this.id}/tokens/${id}`)
        .then((response) => {
            NotificationService.$emit('NOTIFICATION', new Notification(response, 'done'))
            this._reloadTokens()
        })
    }

    addToken (description) {
        const d = { description: description, scope_pull: true, scope_push: true }
        return APIService.post(`project/${this.id}/tokens`, d)
        .then((response) => {
            const token = response.data.token
            this._reloadTokens()
            return token
        })
    }

    addCollaborator (username) {
        const d = { username: username }
        return APIService.post(`project/${this.id}/collaborators`, d)
        .then((response) => {
            this._reloadCollaborators()
        })
    }

    _loadCollaborators () {
        if (this.collaborators) {
            return
        }

        this._reloadCollaborators()
    }

    _reloadCollaborators () {
        return APIService.get(`project/${this.id}/collaborators`)
            .then((collaborators) => {
                store.commit('setCollaborators', { project: this, collaborators: collaborators })
            })
    }

    _loadSecrets () {
        if (this.secrets) {
            return
        }

        this._reloadSecrets()
    }

    _reloadSecrets () {
        return APIService.get(`project/${this.id}/secrets`)
            .then((secrets) => {
                store.commit('setSecrets', { project: this, secrets: secrets })
            })
    }

    _loadTokens () {
        if (this.tokens) {
            return
        }

        this._reloadTokens()
    }

    _reloadTokens () {
        return APIService.get(`project/${this.id}/tokens`)
            .then((tokens) => {
                store.commit('setTokens', { project: this, tokens: tokens })
            })
    }

    _getBuild (number, restartCounter) {
        for (let b of this.builds) {
            if (b.number === number && b.restartCounter === restartCounter) {
                return b
            }
        }
    }

    _addJobs (jobs) {
        if (!jobs) {
            return
        }

        store.commit('addJobs', jobs)
    }
}