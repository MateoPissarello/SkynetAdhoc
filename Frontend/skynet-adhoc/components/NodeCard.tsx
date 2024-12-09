import React, { useEffect, useState } from 'react';
import Modal from '../components/modal';
import laptopImage from '../src/assets/images/laptop.png';
import raspberryImage from '../src/assets/images/raspberry.png';
import styles from '../styles/NodeCard.module.css';

type NodeCardProps = {
    ip: string;
    estado: string;
    ultima_actualizacion: string;
    rowStart: number;
};

type TemperatureData = {
    Temperatura: string;
    Humedad: string;
};
const NodeCard: React.FC<NodeCardProps> = ({ ip, estado, ultima_actualizacion, rowStart }) => {
    const [isModalOpen, setIsModalOpen] = useState(false); // Modal state
    const [socket, setSocket] = useState<WebSocket | null>(null);
    const [tempData, setTempData] = useState<TemperatureData>({
        Temperatura: "N/A",
        Humedad: "N/A",
    });
    useEffect(() => {
        // Crear la conexión WebSocket
        const ws = new WebSocket("ws://192.168.2.11:8001/ws/temperatura");

        // Al recibir mensajes del WebSocket
        ws.onmessage = (event) => {
            const data = JSON.parse(event.data);

            setTempData(data); // Actualiza el estado con los datos del WebSocket
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


    const handleOpenModal = () => setIsModalOpen(true);
    const handleCloseModal = () => setIsModalOpen(false);

    // Determine status indicator and node image
    const statusClass = estado === "Conectado" ? styles.connected : styles.disconnected;
    const nodeImage = ip === "192.168.2.11" ? raspberryImage : laptopImage;

    return (
        <>
            <div
                className={styles.card_container}
                style={{
                    gridRowStart: rowStart,
                    gridRowEnd: rowStart + 1,
                    gridColumnStart: 1,
                    gridColumnEnd: 3,
                }}
            >
                <div className={styles.cardContent}>
                    {/* Image on the left */}
                    <img src={nodeImage} alt="Node" className={styles.nodeImage} />

                    {/* Card content */}
                    <div className={styles.textContainer}>
                        {/* Status and button container */}
                        <div className={styles.statusContainer}>
                            <div className={styles.subtatusContainer}>
                                <div className={`${styles.statusIndicator} ${statusClass}`}></div>
                                <div className={styles.statusText}>{estado}</div>
                            </div>
                            {ip === "192.168.2.11" && estado === "Conectado" && (
                                <button
                                    className={styles.temperatureButton}
                                    onClick={handleOpenModal}
                                >
                                    Temperatura
                                </button>
                            )}
                        </div>

                        {/* IP and last update information */}
                        <h3 className={styles.ip_title}>{ip}</h3>
                        <p><strong>Última Actualización:</strong> {ultima_actualizacion}</p>
                    </div>
                </div>
            </div>

            {/* Modal */}
            <Modal isOpen={isModalOpen} onClose={handleCloseModal} title="DHT11 Data">
                <div className={styles.modalInfo}>
                    <div className={styles.temperatureInfo}>
                        <h3 className={styles.modalTitles}>Temperatura</h3>
                        <p className={styles.modalText}>{tempData.Temperatura}</p>
                    </div>
                    <div className={styles.humidityInfo}>
                        <h3 className={styles.modalTitles}>Humedad</h3>
                        <p className={styles.modalText}>{tempData.Humedad}</p>
                    </div>
                </div>
            </Modal>
        </>
    );
};

export default NodeCard;
