# Box re-brand

`baba_jewellers_box.mp4` is the source jewellery-box clip with the STROILI mark on the
lid replaced by the BABA JEWELLERS logo.

`rebrand_box.py` produced it. The shot is locked off and the lid never moves while it is
seated (frames 0–20 and 219–269), so the logo is placed once in image space at 244 px
wide, centred on the old mark. Per frame the script still has to handle the finger that
crosses the lid and the shadow it casts:

- **Clean plate** — frame 0 with the STROILI mark inpainted out, re-lit each frame by a
  per-channel ratio against frame 0 so the moving shadow keeps its colour.
- **Finger matte** — chromaticity `c = (B-G)/R`, measured as a *change* from frame 0 so
  the printed mark cancels. Shadow shifts `c` by about +0.025; skin swings it to -0.07 and
  the burgundy nail to +0.13. Ramping both ends gives a soft edge that follows the real
  defocus, and the finger is composited back over the logo.
- The logo is lit by the same ratio map, so it darkens under the shadow like ink on card.
- **Black keyline** — gold on a pale pink card needs an edge to hold it, so the logo
  carries a 1.5 px black outline (`OUTLINE_PX`). It is built by dilating the alpha at
  source resolution and area-resampling, and composited premultiplied so the outline
  adds coverage but no colour and the gold is untouched where the two overlap. Much
  past 2 px the counters in JEWELLERS start closing up at this size.

Run from a directory holding `frames.npy` (the decoded source) and `logo_crop.png`
(`baba_jewellers_logo.png` cropped to its alpha bounds), then mux the PNGs with the
source audio.
