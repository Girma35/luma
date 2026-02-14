import { useState } from 'react';
import ConnectStoreModal from './ConnectStoreModal';

interface Props {
  children: React.ReactNode;
  className?: string;
}

export default function ConnectStore({ children, className }: Props) {
  const [open, setOpen] = useState(false);
  return (
    <>
      <button type="button" onClick={() => setOpen(true)} className={className}>
        {children}
      </button>
      <ConnectStoreModal open={open} onClose={() => setOpen(false)} />
    </>
  );
}
