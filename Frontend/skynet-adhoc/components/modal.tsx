import React, { FC, ReactNode } from "react";
import styles from  "../styles/Modal.module.css";

interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  title?: string;
  children: ReactNode;
}

const Modal: FC<ModalProps> = ({ isOpen, onClose, title, children }) => {
  if (!isOpen) return null;

  return (
    <div className={styles.modal_overlay} onClick={onClose}>
      <div className={styles.modal_content} onClick={(e) => e.stopPropagation()}>
        <div className={styles.modal_header}>
          {title && <h2>{title}</h2>}
          <button className={styles.modal_close} onClick={onClose}>
            &times;
          </button>
        </div>
        <div className={styles.modal_body}>{children}</div>
        <div className={styles.modal_footer}>
          <button onClick={onClose}>Close</button>
        </div>
      </div>
    </div>
  );
};

export default Modal;
