import React from 'react'
import ReactDOM from 'react-dom'
import { Router, Route, hashHistory, IndexRoute } from 'react-router'

import MainLayout from './components/MainLayout'
import HomePage from './components/HomePage'

ReactDOM.render((
    <Router history={hashHistory}>
        <Route path="/" component={MainLayout}>
            <IndexRoute component={HomePage} />
            {/*<Route path="settings">
                <Route path="blog" component={BlogSettingsForm} />
                <Route path="account" component={AccountSettingsForm} />
            </Route>*/}
        </Route>
    </Router>
), document.getElementById('root'))

