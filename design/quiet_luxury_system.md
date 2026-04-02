# Quiet Luxury UI System

This system is built around a high-end Italian luxury mood: softened natural fibers, layered warm neutrals, and understated tonal contrast. It is not a generic beige palette and it is not a dashboard language.

## Exact Color System

### Surfaces
- `background.main`: `#F6F3EE`
- `background.secondary`: `#EFE9E1`
- `background.tertiary`: `#E4DDD2`

### Text
- `text.primary`: `#2F2A25`
- `text.secondary`: `#7A7268`

### Accent
- `accent.default`: `#C6A97A`
- `accent.hover`: `#B89664`

### Structure
- `border.soft`: `#E0D8CD`
- `divider.subtle`: `#D6CEC2`

## CSS Variables

```css
:root {
  --bg: #F6F3EE;
  --surface-2: #EFE9E1;
  --surface-3: #E4DDD2;
  --text: #2F2A25;
  --text-soft: #7A7268;
  --accent: #C6A97A;
  --accent-hover: #B89664;
  --border: #E0D8CD;
  --divider: #D6CEC2;
}
```

## Visual Principles
- No pure white and no pure black
- No gradients
- No glassmorphism
- No blue tones anywhere
- Luxury should come from tone-on-tone layering, not from visual effects

## Layout Principles
- One primary action per screen
- Reduce visible controls and hide secondary features
- Align all modules to a single content column
- Use generous whitespace to create calm instead of adding decorative elements

## Component Direction
- Primary button: camel fill with espresso text
- Secondary button: transparent with subtle divider border
- Cards: flat, editorial panels with warm tonal separation
- Inputs: spacious, quiet, and lightly framed
- Expanded details only appear when needed through progressive disclosure
