from pathlib import Path
import re

path = Path('index.html')
asset = Path('images/spinner/out4good-static.webp')
if not asset.exists():
    raise SystemExit('Out4Good static asset is missing')

text = path.read_text(encoding='utf-8')

text = text.replace(
    '<span class="interface-mode__kicker">Featured prison artist / independent gallery</span>',
    '<span class="artist-exhibition__kicker">Featured prison artist / independent gallery</span>'
)

text, removed_html = re.subn(
    r'\n\s*<!-- Interface modes -->\s*<section class="interface-modes interface-modes--top-preview".*?</section>\s*',
    '\n', text, count=1, flags=re.S,
)
if removed_html != 1:
    raise SystemExit(f'Expected one Interface Modes HTML block, removed {removed_html}')

text, removed_js = re.subn(
    r'\n\s*<!-- ===== MODE TRANSITIONS ===== -->\s*<script>.*?</script>\s*',
    '\n', text, count=1, flags=re.S,
)
if removed_js != 1:
    raise SystemExit(f'Expected one mode-transition script, removed {removed_js}')

text, target_count = re.subn(
    r'(<button class="orbit-card(?: penny)?" type="button") data-target="[^"]+"',
    r'\1', text,
)
if target_count < 8:
    raise SystemExit(f'Expected at least 8 orbit data-target attributes, removed {target_count}')

text = text.replace(' let pointerDownCard = null; let pointerDownX = 0; let pointerDownY = 0;', '')
text = text.replace(' pointerDownCard = event.target.closest(".orbit-card"); pointerDownX = event.clientX; pointerDownY = event.clientY;', '')
text, enddrag_count = re.subn(
    r'function endDrag\(event\) \{.*?\} dragSurface\.addEventListener\("pointerup", endDrag\);',
    'function endDrag(event) { if (!isDragging) return; isDragging = false; if (dragSurface.hasPointerCapture(event.pointerId)) { dragSurface.releasePointerCapture(event.pointerId); } window.setTimeout(() => { stage.dataset.dragged = "false"; }, 80); } dragSurface.addEventListener("pointerup", endDrag);',
    text, count=1, flags=re.S,
)
if enddrag_count != 1:
    raise SystemExit(f'Expected one orbit endDrag function, replaced {enddrag_count}')

style_match = re.search(r'<style>(.*?)</style>', text, flags=re.S)
if not style_match:
    raise SystemExit('Style block not found')

def matching_brace(src, opening):
    depth = 1
    i = opening + 1
    quote = None
    while i < len(src):
        ch = src[i]
        if quote:
            if ch == '\\':
                i += 2
                continue
            if ch == quote:
                quote = None
        else:
            if ch in ('"', "'"):
                quote = ch
            elif ch == '{':
                depth += 1
            elif ch == '}':
                depth -= 1
                if depth == 0:
                    return i
        i += 1
    raise ValueError('Unbalanced CSS braces')

def remove_comments(value):
    return re.sub(r'/\*.*?\*/', '', value, flags=re.S)

def clean_selector_header(header):
    comments = re.findall(r'/\*.*?\*/', header, flags=re.S)
    core = remove_comments(header)
    if not core.strip():
        return header
    selectors = core.split(',')
    kept = []
    for selector in selectors:
        if '.interface-mode' in selector or '.interface-modes' in selector or '.orbit-card.is-mode-active' in selector:
            continue
        kept.append(selector)
    if not kept:
        return None
    prefix = ''.join(comments)
    return prefix + ','.join(kept)

def clean_css(src):
    out = []
    i = 0
    while i < len(src):
        opening = src.find('{', i)
        if opening == -1:
            out.append(src[i:])
            break
        header = src[i:opening]
        closing = matching_brace(src, opening)
        body = src[opening + 1:closing]
        code = remove_comments(header).strip()

        if code.startswith('@keyframes') or code.startswith('@-webkit-keyframes'):
            if 'mobileSystem' not in code:
                out.append(header + '{' + body + '}')
        elif code.startswith('@media') or code.startswith('@supports') or code.startswith('@container') or code.startswith('@layer'):
            cleaned_body = clean_css(body)
            if cleaned_body.strip():
                out.append(header + '{' + cleaned_body + '}')
        elif code.startswith('@'):
            out.append(header + '{' + body + '}')
        else:
            cleaned_header = clean_selector_header(header)
            if cleaned_header is not None:
                out.append(cleaned_header + '{' + body + '}')
        i = closing + 1
    return ''.join(out)

css = clean_css(style_match.group(1))
center_css = r'''

    /* ===== STANDALONE TOP-SPINNER CENTER PANEL ===== */
    .orbit-center-panel {
      position: absolute;
      left: 50%;
      top: 48%;
      z-index: 1;
      width: clamp(190px, 56vw, 340px);
      aspect-ratio: 16 / 10;
      overflow: hidden;
      border-radius: 20px;
      background: #020408;
      box-shadow: 0 18px 48px rgba(0, 0, 0, 0.52), inset 0 0 0 1px rgba(182, 255, 0, 0.22);
      transform: translate(-50%, -50%);
      pointer-events: none;
    }

    .orbit-center-panel__image {
      display: block;
      width: 100%;
      height: 100%;
      object-fit: cover;
      object-position: center;
      opacity: 1;
      filter: none;
    }

    .orbit-center-panel__warning {
      position: absolute;
      right: 10px;
      bottom: 10px;
      left: 10px;
      margin: 0;
      padding: 7px 9px;
      border-radius: 999px;
      color: #b6ff00;
      background: rgba(0, 7, 0, 0.74);
      font-size: clamp(0.56rem, 1.4vw, 0.74rem);
      font-weight: 900;
      line-height: 1.3;
      text-align: center;
      text-shadow: 0 0 8px rgba(182, 255, 0, 0.88), 0 0 18px rgba(182, 255, 0, 0.52);
      animation: out4goodWarningPulse 1.8s ease-in-out infinite;
    }

    @keyframes out4goodWarningPulse {
      0%, 100% { opacity: 0.64; text-shadow: 0 0 7px rgba(182, 255, 0, 0.58), 0 0 14px rgba(182, 255, 0, 0.30); }
      50% { opacity: 1; text-shadow: 0 0 11px rgba(182, 255, 0, 1), 0 0 24px rgba(182, 255, 0, 0.72); }
    }

    @media (prefers-reduced-motion: reduce) {
      .orbit-center-panel__warning { animation: none; opacity: 1; }
    }
'''
anchor = '    .orbit-guidance {'
if anchor not in css:
    raise SystemExit('Orbit guidance CSS anchor missing')
css = css.replace(anchor, center_css + '\n' + anchor, 1)
text = text[:style_match.start(1)] + css + text[style_match.end(1):]

artist_anchor = '    .artist-exhibition__header h2 { margin: 8px 0; font-size: clamp(1.7rem,4vw,3rem); }'
artist_kicker_css = '    .artist-exhibition__kicker { display: inline-block; margin: 0; color: var(--pink); font-size: .7rem; font-weight: 900; letter-spacing: .16em; text-transform: uppercase; }\n'
if artist_anchor not in text:
    raise SystemExit('Artist header CSS anchor missing')
text = text.replace(artist_anchor, artist_kicker_css + artist_anchor, 1)

panel_markup = '''            <div class="orbit-center-panel" aria-label="Out4Good re-entry warning">
              <img class="orbit-center-panel__image" src="images/spinner/out4good-static.webp" alt="Out4Good re-entry resources" />
              <p class="orbit-center-panel__warning">out4good is part of the system. Plan your re-entry accordingly...</p>
            </div>

'''
html_anchor = '            <!-- Holo Floor projection system -->'
if 'class="orbit-center-panel"' in text:
    raise SystemExit('A center panel already exists; refusing duplicate insertion')
if html_anchor not in text:
    raise SystemExit('Holo Floor insertion anchor missing')
text = text.replace(html_anchor, panel_markup + html_anchor, 1)

forbidden = ['interface-modes', 'interface-mode ', 'interface-mode\"', 'setInterfaceMode', 'is-mode-active', 'mobileSystem']
leftovers = [token for token in forbidden if token in text]
if leftovers:
    for token in leftovers:
        for number, line in enumerate(text.splitlines(), start=1):
            if token in line:
                print(f'LEFTOVER {token} line {number}: {line[:240]}')
    raise SystemExit('Obsolete interface-mode residue remains: ' + ', '.join(leftovers))
if text.count('class="orbit-center-panel"') != 1:
    raise SystemExit('Center panel count is not exactly one')
if text.count('out4good-static.webp') != 1:
    raise SystemExit('Static Out4Good image reference count is not exactly one')
if 'class="artist-exhibition__kicker"' not in text:
    raise SystemExit('Artist kicker decoupling failed')
if 'class="artist-spinner"' not in text:
    raise SystemExit('Artist spinner was unexpectedly removed')

path.write_text(text, encoding='utf-8')
