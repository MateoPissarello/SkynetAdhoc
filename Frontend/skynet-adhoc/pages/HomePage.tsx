
import React, { useEffect, useState } from 'react';
import styles from '../styles/HomePage.module.css';

import NodeCard from '../components/NodeCard';


type NodeState = {
    estado: string;
    ultima_actualizacion: string;
};

type NodeStates = {
    [ip: string]: NodeState;
};

const HomePage = () => {
    const [nodes, setNodes] = useState<NodeStates>({});
    const [socket, setSocket] = useState<WebSocket | null>(null);
    const [btnStatus, setBtnStatus] = useState<boolean>(true);


    useEffect(() => {
        // Crear la conexión WebSocket
        const ws = new WebSocket("ws://127.0.0.1:8000/ws");

        console.log(nodes)
        // Al recibir mensajes del WebSocket
        ws.onmessage = (event) => {
            const data = JSON.parse(event.data);

            setNodes(data); // Actualiza el estado con los datos del WebSocket
        };

        // Manejar posibles errores de conexión
        ws.onerror = (error) => {
            console.error("WebSocket error:", error);
        };

        // Cuando se cierra la conexión WebSocket
        ws.onclose = () => {
            console.log("WebSocket connection closed");
        };

        // Guardar el socket y limpiarlo cuando el componente se desmonte
        setSocket(ws);
        return () => {
            ws.close(); // Cerrar el WebSocket cuando se desmonte el componente
        };
    }, []);

    const postStartMonitoring = async () => {
        await fetch("http://127.0.0.1:8000/start").then((response) => {
            if (!response.ok) {
                throw new Error('Error en la solicitud');
            }
            return response.json();  // Parseamos la respuesta a JSON
        })
            .then((data) => {
                console.log('Datos recibidos:', data);  // Aquí manejas los datos recibidos
            })
            .catch((error) => {
                console.error('Hubo un problema con la solicitud Fetch:', error);
            });
    }
    const toggleButtonColor = () => {
        const nodes_length = Object.keys(nodes).length;
        if (btnStatus) {
            if (nodes_length === 0){
                postStartMonitoring();
                setBtnStatus(prevStatus => !prevStatus);
            }

        }
    };
    return (
        <>
            <div className={styles.header}>
                <h1 className={styles.title}>SKYNET-ADHOC</h1>
                <button
                    className={`${styles.start_monitoring_button} ${btnStatus ? styles.greenButton : styles.redButton}`}
                    onClick={toggleButtonColor}
                >
                    {btnStatus ? "Iniciar Monitoreo" : "Detener Monitoreo"}
                </button>
            </div>
            <div className={styles.parent_container}>
                <div className={styles.container}>
                    {/* Aquí se recorre y muestra cada nodo */}
                    {Object.entries(nodes).map(([ip, { estado, ultima_actualizacion }], index) => {
                        const rowStart = index + 1; // Asignar fila, la primera tarjeta ocupa la fila 1-2, la segunda 2-3, etc.

                        return (
                            <NodeCard
                                key={ip}
                                ip={ip}
                                estado={estado}
                                ultima_actualizacion={ultima_actualizacion}
                                rowStart={rowStart} // Pasa la fila de inicio como prop
                            />
                        );
                    })}
                </div>

            </div>

        </>
    );
};

export default HomePage;