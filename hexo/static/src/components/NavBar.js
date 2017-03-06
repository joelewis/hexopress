import React from 'react'
import {Link} from 'react-router'

const NavBar = (props) => {
    return (
        <div>  
            <section className="section section-header bg-grey">
                <section className="grid-header container grid-960">
                <nav className="navbar">
                    <section className="navbar-section">
                        <Link href="/"> <span id="brand-logo"> HexoPress </span> </Link>
                    </section>
                    <section className="navbar-section float-right">
                        <div className="dropdown">
                            <a href="#" className="btn btn-primary dropdown-toggle" tabIndex="0">
                                {window.hexopress.user.email} <i className="icon-caret"></i>
                            </a>
                            <ul className="menu">
                                <li className="menu-item">
                                    <a href="/logout">Sign Out</a>
                                    <a href="/logout">Delete Account & Blog</a>
                                </li>
                            </ul>
                        </div>
                    </section>
                </nav>
                </section>
            </section>
        </div>
    )
}

export default NavBar