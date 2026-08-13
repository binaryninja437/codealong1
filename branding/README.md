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
- **Ink colour** — the logo is printed, not overlaid. `INK` is BGR (28, 22, 100), a
  deep maroon carrying the same density as the box's own print (measured at BGR
  25/30/90 off the core of the STROILI mark in frame 0, a warmer brown). It is laid
  down flat like the mark it replaces, premultiplied so the antialiased edges stay
  clean. Gold read as an overlay on this pale card; ink at the printer's density
  reads as part of the lid. Lighter, redder values (around R150) lose authority at
  this size — the mark stops holding its own against the pink.

Run from a directory holding `frames.npy` (the decoded source) and `logo_crop.png`
(`baba_jewellers_logo.png` cropped to its alpha bounds), then mux the PNGs with the
source audio.

# End-card re-brand

`baba_jewellers_ad.mp4` is the necklace ad with the JOWELE end logo replaced by
BABA JEWELLERS. `rebrand_endcard.py` produced it.

The old mark is a static, fully opaque overlay that pops on at frame 253 and holds to
the end; at frame 292 the footage hard-cuts to black behind it. Two measurements made
the job simple:

- **The matte came free.** Frames 292+ are the logo on pure black, so that image *is*
  the mark premultiplied — dividing by its gold plateau (BGR 10/186/234, luma 180)
  gives an exact alpha. Reading the plateau matters: sampling the brightest pixels
  instead picks up antialiasing fringe and yields an alpha that peaks around 0.89,
  which breaks every downstream test.
- **Nothing is composited over the mark.** It looks like the necklace crosses the
  letters, but comparing each frame against the black card inside the opaque core
  shows a mean difference of 8/255 — the chain and pendant thread through the gap
  between the W and the E. So no jewellery matte is needed: paint out the mark's own
  footprint and lay the new logo on top.

Removal is TELEA inpainting of the dilated alpha, which reconstructs the smooth skin
and the fabric diagonal convincingly; grain is added back so the repainted area is not
a smooth patch inside grainy footage. On the black-card frames the same path yields
black, so one code path covers both. The new logo is placed on the old mark's
footprint (467 px wide, centred at 360, 626) in its own gold artwork rather than the
ad's flat yellow — the gradient reads richer on black, and the pendant hangs clear
below the lockup.
