import { createContext, useContext, useState, ReactNode } from 'react'

interface DrawerContextType {
  isOpen: boolean
  openDrawer: () => void
  closeDrawer: () => void
  toggleDrawer: () => void
}

const DrawerContext = createContext<DrawerContextType>({
  isOpen: false,
  openDrawer: () => {},
  closeDrawer: () => {},
  toggleDrawer: () => {},
})

export function DrawerProvider({ children }: { children: ReactNode }) {
  const [isOpen, setIsOpen] = useState(false)
  return (
    <DrawerContext.Provider value={{
      isOpen,
      openDrawer: () => setIsOpen(true),
      closeDrawer: () => setIsOpen(false),
      toggleDrawer: () => setIsOpen(p => !p),
    }}>
      {children}
    </DrawerContext.Provider>
  )
}

export const useDrawer = () => useContext(DrawerContext)
