
import React from 'react';
import styles from '../styles/HomePage.module.css';
const HomePage = () => {
    return(
    <>
        <div className={styles.header}>
            <h1 className={styles.title}>SKYNET-ADHOC</h1>
                
            </div>
        <div style={{"display":"flex", "backgroundColor":"red", "width":"80%", "height":"50rem", "margin":"0 auto" }}>
            <div style={{"display":"grid", "backgroundColor":"blue"}}>
                <h1>Left</h1>
        </div>
        </div>
    </>
    )
}

export default HomePage;