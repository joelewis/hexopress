import React from 'react'
import ReactDOM from 'react-dom'
import { Router, Route, browserHistory, IndexRoute } from 'react-router'

import MainLayout from './components/MainLayout'
import HomePage from './components/HomePage'
import BlogSettingsForm from './components/BlogSettingsForm'
import AccountSettingsForm from './components/AccountSettingsForm'
import FaqPage from './components/FaqPage.js'

import socket from './socket'

// if not logged in, don't render component.
if (window.hexopress) {
    ReactDOM.render((
        <Router history={browserHistory}>
            <Route path="/" component={MainLayout}>
                <IndexRoute getComponent={
                    (location, cb) => {
                        if (window.hexopress.user.accountinfo_filled || hexopress.blog.is_generated) {
                            cb(null, HomePage)
                        } else {
                            cb(null, props => (<AccountSettingsForm settings={hexopress.user} />))
                        }
                    }
                 } />
                <Route path="/app/settings">
                    <Route path="blog" component={() => (<BlogSettingsForm settings={hexopress.blog} />)} />
                    <Route path="account" component={() => (<AccountSettingsForm settings={hexopress.user} />)} />
                </Route>
                <Route path="/app/faq" component={FaqPage} />
            </Route>
        </Router>
    ), document.getElementById('root'))
}


