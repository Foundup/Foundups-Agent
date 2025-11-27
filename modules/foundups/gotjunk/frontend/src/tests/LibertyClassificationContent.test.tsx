import React from 'react';
import { describe, it, expect, vi, afterEach } from 'vitest';
import { fireEvent, render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import { LibertyClassificationContent } from '../../components/LibertyClassificationContent';
import { useLongPress } from '../../hooks/useLongPress';

const noopHandlers: ReturnType<typeof useLongPress> = {
  onPointerDown: () => {},
  onPointerUp: () => {},
  onPointerMove: () => {},
  onPointerCancel: () => {},
  onTouchStart: () => {},
  onTouchEnd: () => {},
  onTouchMove: () => {},
  onTouchCancel: () => {},
  onMouseDown: () => {},
  onMouseUp: () => {},
  onMouseMove: () => {},
  onMouseLeave: () => {},
};

afterEach(() => {
  vi.restoreAllMocks();
});

const renderModalShell = ({
  title,
  helperText,
  helperTextMargin,
  children,
  footer,
  actionSheets,
}: any) => (
  <div>
    <h2>{title}</h2>
    {helperText && <p className={helperTextMargin}>{helperText}</p>}
    <div data-testid="body">{children}</div>
    {footer}
    {actionSheets}
  </div>
);

describe('LibertyClassificationContent', () => {
  it('renders accordion headers', () => {
    render(
      <LibertyClassificationContent
        renderModalShell={renderModalShell}
        onClassify={vi.fn()}
        onCancel={vi.fn()}
        discountLongPress={noopHandlers}
        bidLongPress={noopHandlers}
        discountPercent={75}
        bidDurationHours={72}
      />
    );

    expect(screen.getByText('Stuff!')).toBeInTheDocument();
    expect(screen.getByText('Alert!')).toBeInTheDocument();
    expect(screen.getByText('Food!')).toBeInTheDocument();
    expect(screen.getByText('Shelter!')).toBeInTheDocument();
  });

  it('expands Alert and triggers onClassify for ICE', () => {
    const onClassify = vi.fn();
    render(
      <LibertyClassificationContent
        renderModalShell={renderModalShell}
        onClassify={onClassify}
        onCancel={vi.fn()}
        discountLongPress={noopHandlers}
        bidLongPress={noopHandlers}
        discountPercent={75}
        bidDurationHours={72}
      />
    );

    fireEvent.click(screen.getByText('Alert!'));

    const iceButton = screen.getByText('ICE Alert');
    fireEvent.pointerDown(iceButton);
    fireEvent.pointerUp(iceButton);

    expect(onClassify).toHaveBeenCalled();
    expect(onClassify.mock.calls[0][0]).toBe('ice');
  });
});
